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

**Note**: You will receive a list of queries to the system, and the final output should be an array of strings representing the returned values of all queries. Each query will only call one operation.

Level 1
-------

The basic level of the in-memory database contains records. Each record can be accessed with a unique identifier key of string type. A record may contain several field-value pairs, both of which are of string type.

* `SET <key> <field> <value>` — should insert a field-value pair to the record associated with key. If the field in the record already exists, replace the existing value with the specified value. If the record does not exist, create a new one. This operation should return an empty string.
* `GET <key> <field>` — should return the value contained within field of the record associated with key. If the record or the field doesn't exist, should return an empty string.
* `DELETE <key> <field>` — should remove the field from the record associated with key. Returns "true" if the field was successfully deleted, and "false" if the key or the field do not exist in the database.

### Examples

The example below shows how these operations should work:

| Queries | Explanations |
| --- | --- |
| `["SET", "A", "B", "E"]` | returns ""; database state: `{"A": {"B": "E"}}` |
| `["SET", "A", "C", "F"]` | returns ""; database state: `{"A": {"C": "F", "B": "E"}}` |
| `["GET", "A", "B"]` | returns "E" |
| `["GET", "A", "D"]` | returns "" |
| `["DELETE", "A", "B"]` | returns "true"; database state: `{"A": {"C": "F"}}` |
| `["DELETE", "A", "D"]` | returns "false"; database state: `{"A": {"C": "F"}}` |