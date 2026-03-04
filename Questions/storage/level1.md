# Level 1

The cloud storage system should support file manipulation.

- `ADD_FILE <name> <size>` — should add a new file `name` to the storage. `size` is the amount of memory required in bytes. The current operation fails if a file with the same `name` already exists. Returns `"true"` if the file was added successfully or `"false"` otherwise.

- `GET_FILE_SIZE <name>` — should return a string representing the size of the file `name` if it exists, or an empty string otherwise.

- `DELETE_FILE <name>` — should delete the file `name`. Returns a string representing the deleted file size if the deletion was successful or an empty string if the file does not exist.

## Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
|--------|--------------|
| `["ADD_FILE", "/dir1/dir2/file.txt", "10"]` | returns `"true"`; adds file `"/dir1/dir2/file.txt"` of 10 bytes |
| `["ADD_FILE", "/dir1/dir2/file.txt", "5"]` | returns `"false"`; the file `"/dir1/dir2/file.txt"` already exists |
| `["GET_FILE_SIZE", "/dir1/dir2/file.txt"]` | returns `"10"` |
| `["DELETE_FILE", "/not-existing.file"]` | returns `""`; the file `"/not-existing.file"` does not exist |
| `["DELETE_FILE", "/dir1/dir2/file.txt"]` | returns `"10"` |
| `["GET_FILE_SIZE", "/not-existing.file"]` | returns `""`; the file `"/not-existing.file"` does not exist |

The output should be:
```json
["true", "false", "10", "", "10", ""]
```