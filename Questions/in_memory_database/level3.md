Level 3
-------

Support the timeline of operations and TTL (Time-To-Live) settings for records and fields. Each operation from previous levels now has an alternative version with a timestamp parameter to represent when the operation was executed. For each field-value pair in the database, the TTL determines how long that value will persist before being removed.

Notes:

* Time should always flow forward, so timestamps are guaranteed to strictly increase as operations are executed.
* Each test cannot contain both versions of operations (with and without timestamp). However, you should maintain backward compatibility, so all previously defined methods should work in the same way as before.
* `set_at(key, field, value, timestamp)` — should insert a field-value pair or updates the value of the field in the record associated with key. This operation should return an empty string.
* `set_at_with_ttl(key, field, value, timestamp, ttl)` — should insert a field-value pair or update the value of the field in the record associated with key. Also sets its Time-To-Live starting at timestamp to be ttl. The ttl is the amount of time that this field-value pair should exist in the database, meaning it will be available during this interval: \[timestamp, timestamp + ttl). This operation should return an empty string.
* `delete_at(key, field, timestamp)` — the same as DELETE, but with timestamp of the operation specified. Should return "true" if the field existed and was successfully deleted and "false" if the key didn't exist.
* `get_at(key, field, timestamp)` — the same as GET, but with timestamp of the operation specified.
* `scan_at(key, timestamp)` — the same as SCAN, but with timestamp of the operation specified.
* `scan_by_prefix_at(key, prefix, timestamp)` — the same as SCAN\_BY\_PREFIX, but with timestamp of the operation specified.

### Examples

The examples below show how these operations should work:

| Queries | Explanations |
| --- | --- |
| `set_at_with_ttl("A", "BC", "E", "1", "9")` | returns ""; database state: `{"A": {"BC": "E"}}` where `{"BC": "E"}` expires at timestamp 10 |
| `set_at_with_ttl("A", "BC", "E", "5", "10")` | returns ""; database state: `{"A": {"BC": "E"}}` as field "BC" in record "A" already exists, it was overwritten, and `{"BC": "E"}` now expires at timestamp 15 |
| `set_at("A", "BD", "F", "6")` | returns ""; database state: `{"A": {"BC": E", "BD": "F"}}` where `{"BD": "F"}` does not expire |
| `scan_by_prefix_at("A", "B", "14")` | returns "BC(E), BD(F)" |
| `scan_by_prefix_at("A", "B", "15")` | returns "BD(F)" |

Another example could be:

| Queries | Explanations |
| --- | --- |
| `set_at("A", "B", "C", "1")` | returns ""; database state: `{"A": {"B": "C"}}` |
| `set_at_with_ttl("X", "Y", "Z", "2", "15")` | returns ""; database state: `{"X": {"Y": "Z"}, "A": {"B": "C"}}` where `{"Y": "Z"}` expires at timestamp 17 |
| `get_at("X", "Y", "3")` | returns "Z" |
| `set_at_with_ttl("A", "D", "E", "4", "10")` | returns ""; database state: `{"X": {"Y": "Z"}, "A": {"D": "E", "B": "C"}}` where `{"D": "E"}` expires at timestamp 14 and `{"Y": "Z"}` expires at timestamp 17 |
| `scan_at("A", "13")` | returns "B(C), D(E)" |
| `scan_at("X", "16")` | returns "Y(Z)" |
| `scan_at("X", "17")` | returns ""; Note that all fields in record "X" have expired |
| `delete_at("X", "Y", "20")` | returns "false"; the record "X" was expired at timestamp 17 and can't be deleted. |