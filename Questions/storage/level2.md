# Level 2

Implement an operation for retrieving some statistics about files with a specific prefix.

- `GET_N_LARGEST <prefix> <n>` — should return the string representing the names of the top `n` largest files with names starting with `prefix` in the following format:
  `"<name1>(<size1>), ..., <nameN>(<sizeN>)"`.
  Returned files should be sorted by size in descending order, or in case of a tie, sorted in [lexicographical](https://en.wikipedia.org/wiki/Lexicographical_order) order of the names.
  If there are no such files, return an empty string.
  If the number of such files is less than `n`, all of them should be returned in the specified format.

## Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
|--------|--------------|
| `["ADD_FILE", "/dir/file1.txt", "5"]` | returns `"true"` |
| `["ADD_FILE", "/dir/file2", "20"]` | returns `"true"` |
| `["ADD_FILE", "/dir/deeper/file3.mov", "9"]` | returns `"true"` |
| `["GET_N_LARGEST", "/dir", "2"]` | returns `"/dir/file2(20), /dir/deeper/file3.mov(9)"` |
| `["GET_N_LARGEST", "/dir/file", "3"]` | returns `"/dir/file2(20), /dir/file1.txt(5)"` |
| `["GET_N_LARGEST", "/another_dir", "file.txt"]` | returns `""`; there are no files with the prefix `"/another_dir"` |
| `["ADD_FILE", "/big_file.mp4", "20"]` | returns `"true"` |
| `["GET_N_LARGEST", "/", "2"]` | returns `"/big_file.mp4(20), /dir/file2(20)"`; sizes of files are equal, so returned names are sorted lexicographically |

The output should be:
```json
["true", "true", "true", "/dir/file2(20), /dir/deeper/file3.mov(9)", "/dir/file2(20), /dir/file1.txt(5)", "", "true", "/big_file.mp4(20), /dir/file2(20)"]
```
