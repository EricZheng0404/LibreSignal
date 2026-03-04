# Level 3

Implement support for queries from different users. All users share a common filesystem in the cloud storage system, but each user is assigned a storage capacity limit.

- `ADD_USER <userId> <capacity>` — should add a new user in the system, with `capacity` as their storage limit in bytes. The total size of all files owned by `userId` cannot exceed `capacity`. The operation fails if a user with `userId` already exists. Returns `"true"` if a user was successfully created, or `"false"` otherwise.

- `ADD_FILE_BY <userId> <name> <size>` — should behave in the same way as the `ADD_FILE` from Level 1, but the added file should be owned by the user with `userId`. A new file cannot be added to the storage if doing so would exceed the user's `capacity` limit. Returns a string representing the remaining capacity of the user if the file is added successfully, or an empty string otherwise.

> **Note**: All queries calling the `ADD_FILE` operation implemented during Level 1 are run by the user with `userId = "admin"`, who has unlimited storage capacity.

- `MERGE_USER <userId1> <userId2>` — should merge the account of `userId2` with `userId1`. Ownership of all of `userId2`'s files is transferred to `userId1`, and any remaining storage capacity is also added to `userId1`'s limit. `userId2` is deleted if the merge is successful. Returns a string representing the remaining capacity of `userId1` after merging, or an empty string if one of the users does not exist or `userId1` is equal to `userId2`. It is guaranteed that neither `userId1` nor `userId2` equals `"admin"`.

## Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
|--------|--------------|
| `["ADD_USER", "user1", "200"]` | returns `"true"`; creates user `"user1"` with 200 bytes capacity limit |
| `["ADD_USER", "user1", "100"]` | returns `"false"`; `"user1"` already exists |
| `["ADD_FILE_BY", "user1", "/dir/file.med", "50"]` | returns `"150"` |
| `["ADD_FILE_BY", "user1", "/big.blob", "140"]` | returns `"10"` |
| `["ADD_FILE_BY", "user1", "/file-small", "20"]` | returns `""`; `"user1"` does not have enough storage capacity |
| `["ADD_FILE", "/dir/admin_file", "300"]` | returns `"true"`; done by `"admin"` with unlimited capacity |
| `["ADD_USER", "user2", "110"]` | returns `"true"` |
| `["ADD_FILE_BY", "user2", "/dir/file.med", "45"]` | returns `""`; file already exists and owned by `"user1"` |
| `["ADD_FILE_BY", "user2", "/new_file", "50"]` | returns `"60"` |
| `["MERGE_USER", "user1", "user2"]` | returns `"70"`; transfers ownership of `"/new_file"` to `"user1"` |

The output should be:
```json
["true", "false", "150", "10", "", "true", "true", "", "60", "70"]
```