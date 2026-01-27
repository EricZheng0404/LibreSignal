Level 4
-------

The database should be backed up from time to time. Introduce operations to support backing up and restoring the database state based on timestamps. When restoring, ttl expiration times should be recalculated accordingly.

* `BACKUP <timestamp>` — should save the database state at the specified timestamp, including the remaining ttl for all records and fields. Remaining ttl is the difference between their initial ttl and their current lifespan (the duration between the timestamp of this operation and their initial timestamp). Returns a string representing the number of non-empty non-expired records in the database.
* `RESTORE <timestamp> <timestampToRestore>` — should restore the database from the latest backup before or at timestampToRestore. It's guaranteed that a backup before or at timestampToRestore will exist. Expiration times for restored records and fields should be recalculated according to the timestamp of this operation - since the database timeline always flows forward, restored records and fields should expire after the timestamp of this operation, depending on their remaining ttls at backup. This operation should return an empty string.

### Examples

The example below shows how these operations should work:

| Queries | Explanations |
| --- | --- |
| `["SET_AT_WITH_TTL", "A", "B", "C", "1", "10"]` | returns ""; database state: `{"A": {"B": "C"}}` with lifespan `[1, 11)`, meaning that the record should be deleted at timestamp = 11. |
| `["BACKUP", "3"]` | returns "1"; saves the database state |
| `["SET_AT", "A", "D", "E", "4"]` | returns ""; database state: `{"A": {"D": "E", "B": "C"}}` |
| `["BACKUP", "5"]` | returns "1"; saves the database state |
| `["DELETE_AT", "A", "B", "8"]` | returns "true"; database state: `{"A": {"D": "E"}}` |
| `["BACKUP", "9"]` | returns "1"; saves the database state |
| `["RESTORE", "10", "7"]` | returns ""; restores the database to state of last backup at timestamp = 5: `{"A": {"D": "E", "B": "C"}}` with `{"B": "C"}` expiring at timestamp = 16: Since the initial ttl of the field is 10 and the database was restored to the state at timestamp = 5; this field has had a lifespan of 4 and a remaining ttl of 6, so it will now expire at timestamp = 10 + 6 = 16. |
| `["BACKUP", "11"]` | returns "1"; saves the database state |
| `["SCAN_AT", "A", "15"]` | returns "B(C), D(E)" |
| `["SCAN_AT", "A", "16"]` | returns "D(E)" |

The output should be `["", "1", "", "1", "true", "1", "", "1", "B(C), D(E)", "D(E)"]`.