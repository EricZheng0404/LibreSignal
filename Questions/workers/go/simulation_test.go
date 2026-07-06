package main

import (
	"fmt"
	"reflect"
	"testing"
)

func newTestWorkers() any {
	return &WorkerRegistration{
		w:  make(map[string]*Worker),
		ts: []int{},
	}
}

func callStringMethod(t *testing.T, db any, candidates []string, args ...any) string {
	t.Helper()

	method, methodName := findMethod(db, candidates)
	if !method.IsValid() {
		t.Fatalf("none of the method names exist: %v", candidates)
	}

	methodType := method.Type()
	if methodType.NumIn() != len(args) {
		t.Fatalf("method %s expects %d args, got %d", methodName, methodType.NumIn(), len(args))
	}

	in := make([]reflect.Value, len(args))
	for i, arg := range args {
		targetType := methodType.In(i)
		argValue := reflect.ValueOf(arg)

		if !argValue.IsValid() {
			in[i] = reflect.Zero(targetType)
			continue
		}
		if argValue.Type().AssignableTo(targetType) {
			in[i] = argValue
			continue
		}
		if argValue.Type().ConvertibleTo(targetType) {
			in[i] = argValue.Convert(targetType)
			continue
		}

		t.Fatalf(
			"arg %d for method %s has incompatible type %s (expected %s)",
			i,
			methodName,
			argValue.Type(),
			targetType,
		)
	}

	out := method.Call(in)
	if len(out) == 0 {
		return ""
	}

	first := out[0].Interface()
	if first == nil {
		return ""
	}
	if s, ok := first.(string); ok {
		return s
	}
	return fmt.Sprint(first)
}

func findMethod(db any, candidates []string) (reflect.Value, string) {
	v := reflect.ValueOf(db)
	for _, name := range candidates {
		m := v.MethodByName(name)
		if m.IsValid() {
			return m, name
		}
	}
	return reflect.Value{}, ""
}

func assertStringEqual(t *testing.T, got, want string) {
	t.Helper()
	if got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

// ── helper wrappers ──────────────────────────────────────────────────────────

func workerAdd(t *testing.T, ws any, workerId, position string, compensation int) string {
	t.Helper()
	return callStringMethod(t, ws, []string{"add_worker", "addWorker", "AddWorker"}, workerId, position, compensation)
}

func workerRegister(t *testing.T, ws any, workerId string, timestamp int) string {
	t.Helper()
	return callStringMethod(t, ws, []string{"register", "Register"}, workerId, timestamp)
}

func workerGet(t *testing.T, ws any, workerId string) string {
	t.Helper()
	return callStringMethod(t, ws, []string{"get", "Get"}, workerId)
}

func workerTopN(t *testing.T, ws any, n int, position string) string {
	t.Helper()
	return callStringMethod(t, ws, []string{"top_n_workers", "topNWorkers", "TopNWorkers"}, n, position)
}

func workerPromote(t *testing.T, ws any, workerId, newPosition string, newCompensation, startTimestamp int) string {
	t.Helper()
	return callStringMethod(t, ws, []string{"promote", "Promote"}, workerId, newPosition, newCompensation, startTimestamp)
}

func workerCalcSalary(t *testing.T, ws any, workerId string, startTimestamp, endTimestamp int) string {
	t.Helper()
	return callStringMethod(t, ws, []string{"calc_salary", "calcSalary", "CalcSalary"}, workerId, startTimestamp, endTimestamp)
}

// ── Level 1 ──────────────────────────────────────────────────────────────────

func TestLevel1_add_worker_success(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Middle Developer", 150), "true")
}

func TestLevel1_add_worker_duplicate(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Middle Developer", 150), "true")
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Junior Developer", 100), "false")
}

func TestLevel1_register_enter_and_leave(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Middle Developer", 150), "true")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 10), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 25), "registered")
}

func TestLevel1_register_invalid_worker(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerRegister(t, ws, "Walter", 120), "invalid_request")
}

func TestLevel1_get_basic(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Middle Developer", 150), "true")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 10), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 25), "registered")
	assertStringEqual(t, workerGet(t, ws, "Ashley"), "15")
}

func TestLevel1_get_nonexistent(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerGet(t, ws, "Walter"), "")
}

func TestLevel1_get_no_finished_sessions(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Middle Developer", 150), "true")
	// Worker entered but has not left yet – no finished session.
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 10), "registered")
	assertStringEqual(t, workerGet(t, ws, "Ashley"), "0")
}

func TestLevel1_get_multiple_sessions(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Middle Developer", 150), "true")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 10), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 25), "registered") // session 10-25 = 15
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 40), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 67), "registered") // session 40-67 = 27
	assertStringEqual(t, workerGet(t, ws, "Ashley"), "42")                  // 15 + 27 = 42
}

// Full example from level1.md
func TestLevel1_full_example(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Middle Developer", 150), "true")
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Junior Developer", 100), "false")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 10), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 25), "registered")
	assertStringEqual(t, workerGet(t, ws, "Ashley"), "15")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 40), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 67), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 100), "registered")
	assertStringEqual(t, workerGet(t, ws, "Ashley"), "42")
	assertStringEqual(t, workerGet(t, ws, "Walter"), "")
	assertStringEqual(t, workerRegister(t, ws, "Walter", 120), "invalid_request")
}

// ── Level 2 ──────────────────────────────────────────────────────────────────

func TestLevel2_top_n_workers_basic(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Junior Developer", 120), "true")
	assertStringEqual(t, workerRegister(t, ws, "John", 100), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 150), "registered")
	assertStringEqual(t, workerTopN(t, ws, 1, "Junior Developer"), "John(50)")
}

func TestLevel2_top_n_workers_no_position(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Junior Developer", 120), "true")
	assertStringEqual(t, workerTopN(t, ws, 3, "Middle Developer"), "")
}

func TestLevel2_top_n_workers_less_than_n(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Junior Developer", 120), "true")
	assertStringEqual(t, workerRegister(t, ws, "John", 100), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 150), "registered")
	// n=5 but only 1 worker with that position
	assertStringEqual(t, workerTopN(t, ws, 5, "Junior Developer"), "John(50)")
}

func TestLevel2_top_n_workers_zero_time_included(t *testing.T) {
	ws := newTestWorkers()
	// Worker exists but has no finished sessions – should still appear with time 0.
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Junior Developer", 120), "true")
	assertStringEqual(t, workerTopN(t, ws, 5, "Junior Developer"), "Ashley(0)")
}

func TestLevel2_top_n_workers_tie_alphabetical(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Junior Developer", 120), "true")
	assertStringEqual(t, workerAdd(t, ws, "Jason", "Junior Developer", 120), "true")
	assertStringEqual(t, workerRegister(t, ws, "John", 100), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 150), "registered") // John = 50
	assertStringEqual(t, workerRegister(t, ws, "Jason", 200), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Jason", 250), "registered") // Jason = 50
	// Tie: Jason < John alphabetically → Jason first
	assertStringEqual(t, workerTopN(t, ws, 2, "Junior Developer"), "Jason(50), John(50)")
}

// Full example from level2.md
func TestLevel2_full_example(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Junior Developer", 120), "true")
	assertStringEqual(t, workerAdd(t, ws, "Jason", "Junior Developer", 120), "true")
	assertStringEqual(t, workerAdd(t, ws, "Ashley", "Junior Developer", 120), "true")
	assertStringEqual(t, workerRegister(t, ws, "John", 100), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 150), "registered") // John = 50
	assertStringEqual(t, workerRegister(t, ws, "Jason", 200), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Jason", 250), "registered") // Jason = 50
	assertStringEqual(t, workerRegister(t, ws, "Jason", 275), "registered") // Jason in office
	assertStringEqual(t, workerTopN(t, ws, 5, "Junior Developer"), "Jason(50), John(50), Ashley(0)")
	assertStringEqual(t, workerTopN(t, ws, 1, "Junior Developer"), "Jason(50)")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 400), "registered")
	assertStringEqual(t, workerRegister(t, ws, "Ashley", 500), "registered") // Ashley = 100
	assertStringEqual(t, workerRegister(t, ws, "Jason", 575), "registered")  // Jason = 50 + 300 = 350
	assertStringEqual(t, workerTopN(t, ws, 3, "Junior Developer"), "Jason(350), Ashley(100), John(50)")
	assertStringEqual(t, workerTopN(t, ws, 3, "Middle Developer"), "")
}

// ── Level 3 ──────────────────────────────────────────────────────────────────

func TestLevel3_promote_success(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Middle Developer", 200), "true")
	assertStringEqual(t, workerPromote(t, ws, "John", "Senior Developer", 500, 200), "success")
}

func TestLevel3_promote_invalid_pending(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Middle Developer", 200), "true")
	assertStringEqual(t, workerPromote(t, ws, "John", "Senior Developer", 500, 200), "success")
	// Second promotion before the first one activates
	assertStringEqual(t, workerPromote(t, ws, "John", "Principal Developer", 800, 300), "invalid_request")
}

func TestLevel3_promote_invalid_worker(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerPromote(t, ws, "NonExistent", "Senior Developer", 500, 200), "invalid_request")
}

func TestLevel3_promote_applies_on_next_entry_at_or_after_start(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Middle Developer", 200), "true")
	assertStringEqual(t, workerPromote(t, ws, "John", "Senior Developer", 500, 200), "success")
	// Entry at 150 is before startTimestamp 200 → still Middle Developer
	assertStringEqual(t, workerRegister(t, ws, "John", 150), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 300), "registered")
	// Entry at 325 >= 200 → promotion activates
	assertStringEqual(t, workerRegister(t, ws, "John", 325), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 400), "registered")
	assertStringEqual(t, workerGet(t, ws, "John"), "225") // 150 + 75
	assertStringEqual(t, workerTopN(t, ws, 10, "Senior Developer"), "John(225)")
	assertStringEqual(t, workerTopN(t, ws, 10, "Middle Developer"), "")
}

func TestLevel3_calc_salary_basic(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Middle Developer", 200), "true")
	assertStringEqual(t, workerRegister(t, ws, "John", 100), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 125), "registered") // 25 units × 200 = 5000
	assertStringEqual(t, workerCalcSalary(t, ws, "John", 0, 500), "5000")
}

func TestLevel3_calc_salary_nonexistent(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerCalcSalary(t, ws, "NonExistent", 0, 500), "")
}

func TestLevel3_calc_salary_no_overlap(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Middle Developer", 200), "true")
	assertStringEqual(t, workerRegister(t, ws, "John", 100), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 125), "registered")
	// Query range entirely after all sessions
	assertStringEqual(t, workerCalcSalary(t, ws, "John", 900, 1400), "0")
}

func TestLevel3_calc_salary_partial_overlap(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Middle Developer", 200), "true")
	assertStringEqual(t, workerRegister(t, ws, "John", 100), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 200), "registered") // session 100-200, 100 units
	// Query [150, 500] clips session to [150, 200] = 50 units × 200 = 10000
	assertStringEqual(t, workerCalcSalary(t, ws, "John", 150, 500), "10000")
}

func TestLevel3_calc_salary_open_session_not_counted(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Middle Developer", 200), "true")
	assertStringEqual(t, workerRegister(t, ws, "John", 100), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 125), "registered") // finished: 100-125
	assertStringEqual(t, workerRegister(t, ws, "John", 200), "registered") // entered, not yet left
	// Open session (200-?) must not be counted
	assertStringEqual(t, workerCalcSalary(t, ws, "John", 0, 500), "5000")
}

// Full example from level3.md
func TestLevel3_full_example(t *testing.T) {
	ws := newTestWorkers()
	assertStringEqual(t, workerAdd(t, ws, "John", "Middle Developer", 200), "true")
	assertStringEqual(t, workerRegister(t, ws, "John", 100), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 125), "registered")
	assertStringEqual(t, workerPromote(t, ws, "John", "Senior Developer", 500, 200), "success")
	assertStringEqual(t, workerRegister(t, ws, "John", 150), "registered")
	assertStringEqual(t, workerPromote(t, ws, "John", "Senior Developer", 350, 250), "invalid_request")
	assertStringEqual(t, workerRegister(t, ws, "John", 300), "registered")
	assertStringEqual(t, workerRegister(t, ws, "John", 325), "registered")
	// Sessions finished so far: 100-125 (MD@200), 150-300 (MD@200). Session 325-? open.
	// CalcSalary [0,500]: 25×200 + 150×200 = 5000 + 30000 = 35000
	assertStringEqual(t, workerCalcSalary(t, ws, "John", 0, 500), "35000")
	// Senior Developer time = 0 (session 325-? not finished)
	assertStringEqual(t, workerTopN(t, ws, 3, "Senior Developer"), "John(175)")
	assertStringEqual(t, workerRegister(t, ws, "John", 400), "registered") // session 325-400 (SD@500)
	assertStringEqual(t, workerGet(t, ws, "John"), "250")                  // 25+150+75 = 250
	assertStringEqual(t, workerTopN(t, ws, 10, "Senior Developer"), "John(250)")
	assertStringEqual(t, workerTopN(t, ws, 10, "Middle Developer"), "")
	// CalcSalary [110,350]: clip(100-125)→[110,125]=15×200=3000, clip(150-300)→[150,300]=150×200=30000, clip(325-400)→[325,350]=25×500=12500 → 45500
	assertStringEqual(t, workerCalcSalary(t, ws, "John", 110, 350), "45500")
	assertStringEqual(t, workerCalcSalary(t, ws, "John", 900, 1400), "0")
}
