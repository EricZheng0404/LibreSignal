# Level 4

Implement support to allow users to back up their files.

- `BACKUP_USER <userId>` — should back up the current state of all files owned by `userId` (i.e., file names and sizes).
  The backup is stored on a separate storage system and is not affected by any new file manipulation queries.
  Overwrites any backups for the same user if previous backups exist.
  Returns a string representing the number of backed-up files, or an empty string if `userId` does not exist.

- `RESTORE_USER <userId>` — should restore the state of `userId`'s files to the latest backup.
  If there was no backup, all of `userId`'s files are deleted.
  If a file can’t be restored because another user added another file with the same name, it is ignored.
  Returns a string representing the number of the files that are successfully restored, or an empty string if `userId` does not exist.

> **Note**:
> - `MERGE_USER` does not affect `userId`’s backup, and `userId2` is deleted along with its backup.
> - The `RESTORE_USER` operation does not affect the user's capacity.

## Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
|--------|--------------|
| `["ADD_USER", "user", "100"]` | returns `"true"`; creates `"user"` with 100 bytes capacity limit |
| `["ADD_FILE_BY", "user", "/dir/file1", "50"]` | returns `"50"` |
| `["ADD_FILE_BY", "user", "/file2.txt", "30"]` | returns `"20"` |
| `["RESTORE_USER", "user"]` | returns `"0"`; removes all of `"user"`'s files |
| `["ADD_FILE_BY", "user", "/file3.mp4", "60"]` | returns `"40"` |
| `["ADD_FILE_BY", "user", "/file4.txt", "10"]` | returns `"30"` |
| `["BACKUP_USER", "user"]` | returns `"2"`; backs up all of `"user"`'s files |
| `["DELETE_FILE", "/file3.mp4"]` | returns `"60"` |
| `["DELETE_FILE", "/file4.txt"]` | returns `"10"` |
| `["ADD_FILE_BY", "user", "/dir/file5.new", "20"]` | returns `"80"` |
| `["RESTORE_USER", "user"]` | returns `"1"`; restores `"/file4.txt"` and deletes `"/dir/file5.new"` |

The output should be:
```json
["true", "50", "20", "0", "40", "30", "2", "60", "10", "80", "1"]