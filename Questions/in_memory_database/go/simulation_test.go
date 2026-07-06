package main

import (
	"fmt"
	"reflect"
	"testing"
)

func newTestDB() any {
	return &InMemoryDatabase{
		make(map[string]map[string]*TTLData),
		make(map[string]map[string]map[int64]TTLData),
		[]int64{},
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

func dbSet(t *testing.T, db any, key, field, value string) string {
	t.Helper()
	return callStringMethod(t, db, []string{"set", "Set"}, key, field, value)
}

func dbGet(t *testing.T, db any, key, field string) string {
	t.Helper()
	return callStringMethod(t, db, []string{"get", "Get"}, key, field)
}

func dbDelete(t *testing.T, db any, key, field string) string {
	t.Helper()
	return callStringMethod(t, db, []string{"delete", "Delete"}, key, field)
}

func dbScan(t *testing.T, db any, key string) string {
	t.Helper()
	return callStringMethod(t, db, []string{"scan", "Scan"}, key)
}

func dbScanByPrefix(t *testing.T, db any, key, prefix string) string {
	t.Helper()
	return callStringMethod(
		t,
		db,
		[]string{"scan_by_prefix", "scanByPrefix", "ScanByPrefix"},
		key,
		prefix,
	)
}

func dbSetAt(t *testing.T, db any, key, field, value string, timestamp int) string {
	t.Helper()
	return callStringMethod(t, db, []string{"set_at", "setAt", "SetAt"}, key, field, value, timestamp)
}

func dbSetAtWithTTL(
	t *testing.T,
	db any,
	key, field, value string,
	timestamp, ttl int,
) string {
	t.Helper()
	return callStringMethod(
		t,
		db,
		[]string{"set_at_with_ttl", "setAtWithTTL", "setAtWithTtl", "SetAtWithTTL", "SetAtWithTtl"},
		key,
		field,
		value,
		timestamp,
		ttl,
	)
}

func dbDeleteAt(t *testing.T, db any, key, field string, timestamp int) string {
	t.Helper()
	return callStringMethod(t, db, []string{"delete_at", "deleteAt", "DeleteAt"}, key, field, timestamp)
}

func dbGetAt(t *testing.T, db any, key, field string, timestamp int) string {
	t.Helper()
	return callStringMethod(t, db, []string{"get_at", "getAt", "GetAt"}, key, field, timestamp)
}

func dbScanAt(t *testing.T, db any, key string, timestamp int) string {
	t.Helper()
	return callStringMethod(t, db, []string{"scan_at", "scanAt", "ScanAt"}, key, timestamp)
}

func dbScanByPrefixAt(t *testing.T, db any, key, prefix string, timestamp int) string {
	t.Helper()
	return callStringMethod(
		t,
		db,
		[]string{"scan_by_prefix_at", "scanByPrefixAt", "ScanByPrefixAt"},
		key,
		prefix,
		timestamp,
	)
}

func dbBackup(t *testing.T, db any, timestamp int) string {
	t.Helper()
	return callStringMethod(t, db, []string{"backup", "Backup"}, timestamp)
}

func dbRestore(t *testing.T, db any, timestamp, timestampToRestore int) string {
	t.Helper()
	return callStringMethod(
		t,
		db,
		[]string{"restore", "Restore"},
		timestamp,
		timestampToRestore,
	)
}

func TestLevel1_test_set_and_get(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSet(t, db, "user1", "name", "Alice"), "")
	assertStringEqual(t, dbSet(t, db, "user1", "age", "30"), "")
	assertStringEqual(t, dbGet(t, db, "user1", "name"), "Alice")
	assertStringEqual(t, dbGet(t, db, "user1", "age"), "30")
}

func TestLevel1_test_set_overwrite(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSet(t, db, "user1", "name", "Alice"), "")
	assertStringEqual(t, dbSet(t, db, "user1", "name", "Bob"), "")
	assertStringEqual(t, dbGet(t, db, "user1", "name"), "Bob")
}

func TestLevel1_test_get_non_existent(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbGet(t, db, "user1", "field"), "")
	assertStringEqual(t, dbSet(t, db, "user1", "name", "Alice"), "")
	assertStringEqual(t, dbGet(t, db, "user1", "non_existent"), "")
}

func TestLevel1_test_delete(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSet(t, db, "user1", "name", "Alice"), "")
	assertStringEqual(t, dbDelete(t, db, "user1", "name"), "true")
	assertStringEqual(t, dbGet(t, db, "user1", "name"), "")
	assertStringEqual(t, dbDelete(t, db, "user1", "name"), "false")
	assertStringEqual(t, dbDelete(t, db, "non_existent", "field"), "false")
}

func TestLevel2_test_scan(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSet(t, db, "user1", "name", "Alice"), "")
	assertStringEqual(t, dbSet(t, db, "user1", "age", "30"), "")
	assertStringEqual(t, dbSet(t, db, "user1", "city", "NY"), "")
	assertStringEqual(t, dbSet(t, db, "user1", "abc", "123"), "")
	assertStringEqual(t, dbScan(t, db, "user1"), "abc(123), age(30), city(NY), name(Alice)")
	assertStringEqual(t, dbScan(t, db, "non_existent"), "")
}

func TestLevel2_test_scan_by_prefix(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSet(t, db, "user1", "name", "Alice"), "")
	assertStringEqual(t, dbSet(t, db, "user1", "age", "30"), "")
	assertStringEqual(t, dbSet(t, db, "user1", "city", "NY"), "")
	assertStringEqual(t, dbSet(t, db, "user1", "abc", "123"), "")
	assertStringEqual(t, dbScanByPrefix(t, db, "user1", "a"), "abc(123), age(30)")
	assertStringEqual(t, dbScanByPrefix(t, db, "user1", "n"), "name(Alice)")
	assertStringEqual(t, dbScanByPrefix(t, db, "user1", "xyz"), "")
}

func TestLevel3_test_set_at_and_get_at(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAt(t, db, "user1", "name", "Alice", 100), "")
	assertStringEqual(t, dbSetAt(t, db, "user1", "age", "30", 101), "")
	assertStringEqual(t, dbGetAt(t, db, "user1", "name", 102), "Alice")
	assertStringEqual(t, dbGetAt(t, db, "user1", "age", 103), "30")
}

func TestLevel3_test_get_at_non_existent(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbGetAt(t, db, "user2", "name", 100), "")
	assertStringEqual(t, dbGetAt(t, db, "user1", "non_existent", 101), "")
}

func TestLevel3_test_set_at_with_ttl_and_get_at(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "name", "Alice", 100, 10), "")
	assertStringEqual(t, dbGetAt(t, db, "user1", "name", 105), "Alice")
	assertStringEqual(t, dbGetAt(t, db, "user1", "name", 110), "")
	assertStringEqual(t, dbGetAt(t, db, "user1", "name", 115), "")
}

func TestLevel3_test_set_at_with_ttl_overwrite_without_expiry(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "name", "Alice", 100, 10), "")
	assertStringEqual(t, dbSetAt(t, db, "user1", "name", "Bob", 105), "")
	assertStringEqual(t, dbGetAt(t, db, "user1", "name", 110), "Bob")
	assertStringEqual(t, dbGetAt(t, db, "user1", "name", 140), "Bob")
}

func TestLevel3_test_set_at_with_ttl_overwrite_with_expiry(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "name", "Alice", 100, 10), "")
	assertStringEqual(t, dbGetAt(t, db, "user1", "name", 105), "Alice")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "name", "Bob", 106, 10), "")
	assertStringEqual(t, dbGetAt(t, db, "user1", "name", 110), "Bob")
	assertStringEqual(t, dbGetAt(t, db, "user1", "name", 117), "")
}

func TestLevel3_test_set_at_with_ttl_and_get_all(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "name", "Alice", 100, 10), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "age", "30", 101, 5), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "city", "NY", 102, 15), "")
	assertStringEqual(t, dbGet(t, db, "user1", "name"), "Alice")
	assertStringEqual(t, dbGet(t, db, "user1", "age"), "30")
	assertStringEqual(t, dbGet(t, db, "user1", "city"), "NY")
}

func TestLevel3_test_scan_at(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "name", "Alice", 100, 10), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "age", "30", 101, 5), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "city", "NY", 102, 15), "")
	assertStringEqual(t, dbScanAt(t, db, "user1", 105), "age(30), city(NY), name(Alice)")
	assertStringEqual(t, dbScanAt(t, db, "user1", 106), "city(NY), name(Alice)")
	assertStringEqual(t, dbScanAt(t, db, "user1", 110), "city(NY)")
	assertStringEqual(t, dbScanAt(t, db, "user1", 116), "city(NY)")
	assertStringEqual(t, dbScanAt(t, db, "user1", 117), "")
}

func TestLevel3_test_scan(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "name", "Alice", 100, 10), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "age", "30", 101, 5), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "city", "NY", 102, 15), "")
	assertStringEqual(t, dbScan(t, db, "user1"), "age(30), city(NY), name(Alice)")
}

func TestLevel3_test_scan_by_prefix_at(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "name", "Alice", 100, 10), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "age", "30", 101, 5), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "city", "NY", 102, 15), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "nationality", "free_country", 103, 5), "")
	assertStringEqual(t, dbScanByPrefixAt(t, db, "user1", "a", 105), "age(30)")
	assertStringEqual(t, dbScanByPrefixAt(t, db, "user1", "a", 106), "")
	assertStringEqual(t, dbScanByPrefixAt(t, db, "user1", "n", 107), "name(Alice), nationality(free_country)")
	assertStringEqual(t, dbScanByPrefixAt(t, db, "user1", "n", 109), "name(Alice)")
}

func TestLevel3_test_scan_by_prefix(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "name", "Alice", 100, 10), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "age", "30", 101, 5), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "city", "NY", 102, 15), "")
	assertStringEqual(t, dbSetAtWithTTL(t, db, "user1", "nationality", "free_country", 103, 5), "")
	assertStringEqual(t, dbScanByPrefix(t, db, "user1", "a"), "age(30)")
	assertStringEqual(t, dbScanByPrefix(t, db, "user1", "n"), "name(Alice), nationality(free_country)")
}

func TestLevel4_test_backup_returns_count(t *testing.T) {
	db := newTestDB()
	assertStringEqual(t, dbSetAtWithTTL(t, db, "A", "B", "C", 1, 10), "")
	assertStringEqual(t, dbBackup(t, db, 3), "1")
}

func TestLevel4_test_backup_excludes_expire(t *testing.T) {
	db := newTestDB()
	_ = dbSetAtWithTTL(t, db, "A", "B", "C", 1, 10)
	assertStringEqual(t, dbBackup(t, db, 12), "0")
}

func TestLevel4_test_restore_from_spec_example(t *testing.T) {
	db := newTestDB()
	_ = dbSetAtWithTTL(t, db, "A", "B", "C", 1, 10)
	_ = dbBackup(t, db, 3)
	_ = dbSetAt(t, db, "A", "D", "E", 4)
	_ = dbBackup(t, db, 5)
	_ = dbDeleteAt(t, db, "A", "B", 8)
	_ = dbBackup(t, db, 9)
	_ = dbRestore(t, db, 10, 7)

	assertStringEqual(t, dbSetAt(t, db, "B", "C", "D", 11), "")
	assertStringEqual(t, dbScanAt(t, db, "A", 15), "B(C), D(E)")
	assertStringEqual(t, dbScanAt(t, db, "A", 16), "D(E)")
	assertStringEqual(t, dbScanAt(t, db, "B", 17), "C(D)")
}
