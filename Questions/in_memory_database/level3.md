Level 3
-------

Support the timeline of operations and TTL (Time-To-Live) settings for records and fields. Each operation from previous levels now has an alternative version with a timestamp parameter to represent when the operation was executed. For each field-value pair in the database, the TTL determines how long that value will persist before being removed.

Notes:

* Time should always flow forward, so timestamps are guaranteed to strictly increase as operations are executed.
* Each test cannot contain both versions of operations (with and without timestamp). However, you should maintain backward compatibility, so all previously defined methods should work in the same way as before.
* `SET_AT <key> <field> <value> <timestamp>` — should insert a field-value pair or updates the value of the field in the record associated with key. This operation should return an empty string.
* `SET_AT_WITH_TTL <key> <field> <value> <timestamp> <ttl>` — should insert a field-value pair or update the value of the field in the record associated with key. Also sets its Time-To-Live starting at timestamp to be ttl. The ttl is the amount of time that this field-value pair should exist in the database, meaning it will be available during this interval: \[timestamp, timestamp + ttl). This operation should return an empty string.
* `DELETE_AT <key> <field> <timestamp>` — the same as DELETE, but with timestamp of the operation specified. Should return "true" if the field existed and was successfully deleted and "false" if the key didn't exist.
* `GET_AT <key> <field> <timestamp>` — the same as GET, but with timestamp of the operation specified.
* `SCAN_AT <key> <timestamp>` — the same as SCAN, but with timestamp of the operation specified.
* `SCAN_BY_PREFIX_AT <key> <prefix> <timestamp>` — the same as SCAN\_BY\_PREFIX, but with timestamp of the operation specified.

### Examples

The examples below show how these operations should work:

| Queries | Explanations |
| --- | --- |
| `["SET_AT_WITH_TTL", "A", "BC", "E", "1", "9"]` | returns ""; database state: `{"A": {"BC": "E"}}` where `{"BC": "E"}` expires at timestamp 10 |
| `["SET_AT_WITH_TTL", "A", "BC", "E", "5", "10"]` | returns ""; database state: `{"A": {"BC": "E"}}` as field "BC" in record "A" already exists, it was overwritten, and `{"BC": "E"}` now expires at timestamp 15 |
| `["SET_AT", "A", "BD", "F", "5"]` | returns ""; database state: `{"A": {"BC": E", "BD": "F"}}` where `{"BD": "F"}` does not expire |
| `["SCAN_BY_PREFIX_AT", "A", "B", "14"]` | returns "BC(E), BD(F)" |
| `["SCAN_BY_PREFIX_AT", "A", "B", "15"]` | returns "BD(F)" |

The output should be `["", "", "", "BC(E), BD(F)", "BD(F)"]`.

Another example could be:

| Queries | Explanations |
| --- | --- |
| `["SET_AT", "A", "B", "C", "1"]` | returns ""; database state: `{"A": {"B": "C"}}` |
| `["SET_AT_WITH_TTL", "X", "Y", "Z", "2", "15"]` | returns ""; database state: `{"X": {"Y": "Z"}, "A": {"B": "C"}}` where `{"Y": "Z"}` expires at timestamp 17 |
| `["GET_AT", "X", "Y", "3"]` | returns "Z" |
| `["SET_AT_WITH_TTL", "A", "D", "E", "4", "10"]` | returns ""; database state: `{"X": {"Y": "Z"}, "A": {"D": "E", "B": "C"}}` where `{"D": "E"}` expires at timestamp 14 and `{"Y": "Z"}` expires at timestamp 17 |
| `["SCAN_AT", "A", "13"]` | returns "B(C), D(E)" |
| `["SCAN_AT", "X", "16"]` | returns "Y(Z)" |
| `["SCAN_AT", "X", "17"]` | returns ""; Note that all fields in record "X" have expired |
| `["DELETE_AT", "X", "Y", "20"]` | returns "false"; the record "X" was expired at timestamp 17 and can't be deleted. |

The output should be `["", "", "Z", "", "B(C), D(E)", "Y(Z)", "", "false"]`.