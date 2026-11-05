"""
LibreSignal web UI server.

A tiny, dependency-free (stdlib only) HTTP server that exposes the practice
questions in ``Questions/`` to a browser-based IDE: read the level specs, edit
``simulation.py``, run each level's pytest suite and see the results.

Usage (from the repository root):

    python ui/server.py            # http://127.0.0.1:8000
    python ui/server.py --port 9000 --open
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
import webbrowser
import xml.etree.ElementTree as ET
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = ROOT / "Questions"
STATIC_DIR = Path(__file__).resolve().parent / "static"
TEST_TIMEOUT_SECONDS = 30
MAX_BODY_BYTES = 2 * 1024 * 1024

LEVEL_FILE_RE = re.compile(r"^level(\d+)\.md$")
LEVEL_CLASS_RE = re.compile(r"TestLevel(\d+)")

ICONS = {
    "bank_system": "🏦",
    "in_memory_database": "🗄️",
    "storage": "☁️",
    "workers": "👷",
}


# --------------------------------------------------------------------------- #
# Question discovery
# --------------------------------------------------------------------------- #
class Question:
    def __init__(self, path: Path):
        self.path = path
        self.id = path.name

    @property
    def title(self) -> str:
        return self.id.replace("_", " ").title()

    @property
    def level_files(self) -> dict[int, Path]:
        levels = {}
        for f in self.path.iterdir():
            m = LEVEL_FILE_RE.match(f.name)
            if m:
                levels[int(m.group(1))] = f
        return dict(sorted(levels.items()))

    @property
    def simulation_file(self) -> Path:
        return self.path / "simulation.py"

    @property
    def solution_file(self) -> Path:
        return self.path / "simulation_solution.py"

    @property
    def test_file(self) -> Path | None:
        tests = sorted(self.path.glob("test_*.py"))
        return tests[0] if tests else None

    def summary(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "icon": ICONS.get(self.id, "🧩"),
            "levels": list(self.level_files.keys()),
            "has_simulation": self.simulation_file.exists(),
            "has_tests": self.test_file is not None,
            "has_solution": self.solution_file.exists(),
        }


def list_questions() -> list[Question]:
    if not QUESTIONS_DIR.is_dir():
        return []
    return [
        Question(p)
        for p in sorted(QUESTIONS_DIR.iterdir())
        if p.is_dir() and not p.name.startswith((".", "_"))
    ]


def find_question(qid: str) -> Question | None:
    # Only ever resolve to a known directory name — never a user-built path.
    for q in list_questions():
        if q.id == qid:
            return q
    return None


# --------------------------------------------------------------------------- #
# Test runner
# --------------------------------------------------------------------------- #
def run_tests(question: Question, level: int | None) -> dict:
    test_file = question.test_file
    if test_file is None:
        return {"ok": False, "error": "This question has no test suite yet."}

    target = str(test_file.relative_to(ROOT))
    if level is not None:
        target += f"::TestLevel{level}"

    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.xml"
        cmd = [
            sys.executable, "-m", "pytest", target,
            "-q", "--tb=short", "--no-header",
            "-p", "no:cacheprovider",
            f"--junitxml={report}",
        ]
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            proc = subprocess.run(
                cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                timeout=TEST_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "error": f"Tests timed out after {TEST_TIMEOUT_SECONDS}s "
                         "(infinite loop?).",
            }

        output = (proc.stdout + proc.stderr).strip()
        tests = parse_junit(report) if report.exists() else []

    levels: dict[int, dict] = {}
    for t in tests:
        lv = levels.setdefault(t["level"], {"passed": 0, "total": 0})
        lv["total"] += 1
        lv["passed"] += t["status"] == "passed"

    return {
        "ok": True,
        "exit_code": proc.returncode,
        "tests": tests,
        "levels": {str(k): v for k, v in sorted(levels.items())},
        "passed": sum(t["status"] == "passed" for t in tests),
        "total": len(tests),
        "output": output[-20000:],
    }


def parse_junit(path: Path) -> list[dict]:
    try:
        tree = ET.parse(path)
    except ET.ParseError:
        return []
    results = []
    for case in tree.iter("testcase"):
        classname = case.get("classname", "")
        m = LEVEL_CLASS_RE.search(classname)
        level = int(m.group(1)) if m else 0
        status, message, details = "passed", "", ""
        for tag in ("failure", "error", "skipped"):
            node = case.find(tag)
            if node is not None:
                status = {"failure": "failed", "error": "error",
                          "skipped": "skipped"}[tag]
                message = node.get("message", "")
                details = (node.text or "").strip()
                break
        results.append({
            "name": case.get("name", ""),
            "class": classname.rsplit(".", 1)[-1],
            "level": level,
            "status": status,
            "time": float(case.get("time", 0) or 0),
            "message": message,
            "details": details,
        })
    return results


# --------------------------------------------------------------------------- #
# HTTP layer
# --------------------------------------------------------------------------- #
class Handler(BaseHTTPRequestHandler):
    server_version = "LibreSignal/1.0"

    # ---- helpers ----
    def log_message(self, fmt, *args):  # quieter logs
        sys.stderr.write("  %s %s\n" % (self.command, self.path))

    def send_json(self, data, status=HTTPStatus.OK):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status, message):
        self.send_json({"ok": False, "error": message}, status)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY_BYTES:
            raise ValueError("Request body too large")
        raw = self.rfile.read(length) if length else b"{}"
        data = json.loads(raw or b"{}")
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")
        return data

    def route(self):
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        return parts

    # ---- verbs ----
    def do_GET(self):
        parts = self.route()
        if not parts or parts[0] != "api":
            return self.serve_static(parts)

        if parts == ["api", "questions"]:
            return self.send_json([q.summary() for q in list_questions()])

        if len(parts) >= 3 and parts[1] == "questions":
            q = find_question(parts[2])
            if q is None:
                return self.send_error_json(HTTPStatus.NOT_FOUND, "Unknown question")
            if len(parts) == 3:
                return self.send_json({
                    **q.summary(),
                    "specs": {str(n): f.read_text(encoding="utf-8")
                              for n, f in q.level_files.items()},
                    "code": q.simulation_file.read_text(encoding="utf-8")
                    if q.simulation_file.exists() else None,
                })
            if parts[3:] == ["solution"] and q.solution_file.exists():
                return self.send_json({"code": q.solution_file.read_text(encoding="utf-8")})
            if parts[3:] == ["tests"] and q.test_file:
                return self.send_json({
                    "name": q.test_file.name,
                    "code": q.test_file.read_text(encoding="utf-8"),
                })
        self.send_error_json(HTTPStatus.NOT_FOUND, "Not found")

    def do_PUT(self):
        parts = self.route()
        if len(parts) == 4 and parts[:2] == ["api", "questions"] and parts[3] == "code":
            q = find_question(parts[2])
            if q is None or not q.simulation_file.exists():
                return self.send_error_json(HTTPStatus.NOT_FOUND, "Unknown question")
            try:
                code = self.read_json().get("code")
            except ValueError as e:
                return self.send_error_json(HTTPStatus.BAD_REQUEST, str(e))
            if not isinstance(code, str):
                return self.send_error_json(HTTPStatus.BAD_REQUEST, "Missing 'code'")
            q.simulation_file.write_text(code, encoding="utf-8")
            return self.send_json({"ok": True})
        self.send_error_json(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self):
        parts = self.route()
        if len(parts) == 4 and parts[:2] == ["api", "questions"] and parts[3] == "run":
            q = find_question(parts[2])
            if q is None:
                return self.send_error_json(HTTPStatus.NOT_FOUND, "Unknown question")
            try:
                body = self.read_json()
            except ValueError as e:
                return self.send_error_json(HTTPStatus.BAD_REQUEST, str(e))
            level = body.get("level")
            if level is not None and (not isinstance(level, int) or level < 1):
                return self.send_error_json(HTTPStatus.BAD_REQUEST, "Bad level")
            code = body.get("code")
            if isinstance(code, str) and q.simulation_file.exists():
                q.simulation_file.write_text(code, encoding="utf-8")
            return self.send_json(run_tests(q, level))
        self.send_error_json(HTTPStatus.NOT_FOUND, "Not found")

    # ---- static files ----
    def serve_static(self, parts):
        rel = "/".join(parts) or "index.html"
        target = (STATIC_DIR / rel).resolve()
        if STATIC_DIR not in target.parents or not target.is_file():
            target = STATIC_DIR / "index.html"
        body = target.read_bytes()
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="LibreSignal web UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--open", action="store_true", help="open a browser tab")
    args = parser.parse_args()

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    print(f"🚦 LibreSignal UI running at {url}  (Ctrl+C to stop)")
    if args.open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
