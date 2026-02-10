In-memory Database
==================

Requirements
------------

Your task is to implement a simplified version of an in-memory database. Plan your design according to the level specifications below:

* **Level 1**: In-memory database should support basic operations to manipulate records, fields, and values within fields.
* **Level 2**: In-memory database should support displaying a specific record's fields based on a filter.
* **Level 3**: In-memory database should support TTL (Time-To-Live) configurations on database records.
* **Level 4**: In-memory database should support backup and restore functionality.

To move to the next level, you need to pass all the tests at this level.


Level 1
-------

The basic level of the in-memory database contains records. Each record can be accessed with a unique identifier key of string type. A record may contain several field-value pairs, both of which are of string type.

* `set(key, field, value)` — should insert a field-value pair to the record associated with key. If the field in the record already exists, replace the existing value with the specified value. If the record does not exist, create a new one. This operation should return an empty string.
* `get(key, field)` — should return the value contained within field of the record associated with key. If the record or the field doesn't exist, should return an empty string.
* `delete(key, field)` — should remove the field from the record associated with key. Returns string "true" if the field was successfully deleted, and "false" if the key or the field do not exist in the database.

### Examples

The example below shows how these operations should work:

| Queries | Explanations |
| --- | --- |
| `set("A", "B", "E")` | returns ""; database state: `{"A": {"B": "E"}}` |
| `set("A", "C", "F")` | returns ""; database state: `{"A": {"C": "F", "B": "E"}}` |
| `get("A", "B")` | returns "E" |
| `get("A", "D")` | returns "" |
| `delete("A", "B")` | returns "true"; database state: `{"A": {"C": "F"}}` |
| `delete("A", "D")` | returns "false"; database state: `{"A": {"C": "F"}}` |