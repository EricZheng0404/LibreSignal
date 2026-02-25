Level 2
-------

The database should support displaying data based on filters. Introduce an operation to support printing some fields of a record.

* `scan(key)` — should return a string representing the fields of a record associated with key. The returned string should be in the following format "&lt;field1&gt;(&lt;value1&gt;), &lt;field2&gt;(&lt;value2&gt;), ...", where fields are sorted lexicographically. If the specified record does not exist, returns an empty string.
* `scan_by_prefix(key, prefix)` — should return a string representing some fields of a record associated with key. Specifically, only fields that start with prefix should be included. The returned string should be in the same format as in the SCAN operation with fields sorted in lexicographical order.

### Examples

The example below shows how these operations should work:

| Queries | Explanations |
| --- | --- |
| `set("A", "BC", "E")` | returns ""; database state: `{"A": {"BC": "E"}}` |
| `set("A", "BD", "F")` | returns ""; database state: `{"A": {"BC": "E", "BD": "F"}}` |
| `set("A", "C", "G")` | returns ""; database state: `{"A": {"BC": "E", "BD": "F", "C": "G"}}` |
| `scan_by_prefix("A", "B")` | returns "BC(E), BD(F)" |
| `scan("A")` | returns "BC(E), BD(F), C(G)" |
| `scan_by_prefix("B", "B")` | returns "" |
