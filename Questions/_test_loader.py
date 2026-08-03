"""Shared helpers for loading a question's implementation under test."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path


def load_class(test_file: str, class_name: str):
    """Load ``class_name`` from the simulation module next to ``test_file``.

    Set SIMULATION_MODULE=simulation_solution to run a suite against the
    reference implementation instead of the editable exercise file.
    """
    module_name = os.environ.get("SIMULATION_MODULE", "simulation")
    if module_name.endswith(".py"):
        module_name = module_name[:-3]

    module_path = Path(test_file).resolve().parent / f"{module_name}.py"
    if not module_path.exists():
        raise ImportError(f"Cannot find module under test: {module_path}")

    spec_name = f"_libresignal_{module_path.parent.name}_{module_name}"
    spec = importlib.util.spec_from_file_location(spec_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module under test: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise ImportError(
            f"{module_path} does not define {class_name}"
        ) from exc
