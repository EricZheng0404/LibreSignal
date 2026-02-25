Level 4
-------

The database should be backed up from time to time. Introduce operations to support backing up and restoring the database state based on timestamps. When restoring, ttl expiration times should be recalculated accordingly.

* `backup(timestamp)` — should save the database state at the specified timestamp, including the remaining lifespan for all records and fields. Remaining lifespan is the duration between the timestamp of this operation and their expiry timestamp. Returns a string representing the number of non-empty non-expired records (the number of keys) in the database.
* `restore(timestamp, timestampToRestore)` — should restore the database from the latest backup before or at timestampToRestore. It's guaranteed that a backup before or at timestampToRestore will exist. Expiration times for restored records and fields should be recalculated according to the timestamp of this operation - since the database timeline always flows forward, restored records and fields should expire after the timestamp of this operation, depending on their remaining ttls at backup. This operation should return an empty string.

### Examples

The example below shows how these operations should work:

| Queries | Explanations |
| --- | --- |
| `set_at_with_ttl("A", "B", "C", "1", "10")` | returns ""; database state: `{"A": {"B": "C"}}` with lifespan `[1, 11)`, meaning that the record should be deleted at timestamp = 11. |
| `backup("3")` | returns "1"; saves the database state |
| `set_at("A", "D", "E", "4")` | returns ""; database state: `{"A": {"D": "E", "B": "C"}}` |
| `backup("5")` | returns "1"; saves the database state |
| `delete_at("A", "B", "8")` | returns "true"; database state: `{"A": {"D": "E"}}` |
| `backup("9")` | returns "1"; saves the database state |
| `restore("10", "7")` | returns ""; restores the database to state of last backup at timestamp = 5: `{"A": {"D": "E", "B": "C"}}` with `{"B": "C"}` expiring at timestamp = 16: Since the initial ttl of the field is 10 and the database was restored to the state at timestamp = 5; this field has had a lifespan of 4 and a remaining ttl of 6, so it will now expire at timestamp = 10 + 6 = 16. |
| `set_at("B", "C", "D", "11")` | returns ""; database state: `{"A": {"D": "E", "B": "C"}, "B": {"C": "D"}}` |
| `backup("12")` | returns "2" because we have two keys in the database; saves the database state |
| `scan_at("A", "15")` | returns "B(C), D(E)" |
| `scan_at("A", "16")` | returns "D(E)" |
| `scan_at("B", "17")` | returns "C(D)" |