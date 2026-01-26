## Instructions

Your task is to implement a simplified version of a banking system. All operations that should be supported are listed below.

Solving this task consists of several levels. In real test, a subsequent level is opened when the current level tests are correct. You always have access to the data for the current and all previous levels.

## Requirements

Your task is to implement a simplified version of a banking system. Plan your design according to the level specifications below:

*   **Level 1:** The banking system should support creating new accounts, depositing money into accounts, and transferring money between two accounts.
*   **Level 2:** The banking system should support ranking accounts based on outgoing transactions.
*   **Level 3:** The banking system should allow scheduling payments with cashback and checking the status of scheduled payments.
*   **Level 4:** The banking system should support merging two accounts while retaining both accounts’ balance and transaction histories.

To move to the next level, you need to pass all the tests at this level.

## Note

All operations will have a `timestamp` parameter — a stringified timestamp in milliseconds. It is guaranteed that all timestamps are unique and are in a range from `1` to `10^9`. Operations will be given in order of strictly increasing timestamps.

## Level 1

Initially, the banking system does not contain any accounts, so implement operations to allow account creation, deposits, and transfers between 2 different accounts.

*   `create_account(self, timestamp: int, account_id: str) -> bool` — should create a new account with the given identifier if it doesn’t already exist. Returns `True` if the account was successfully created or `False` if an account with `account_id` already exists.
*   `deposit(self, timestamp: int, account_id: str, amount: int) -> int | None` — should deposit the given `amount` of money to the specified account `account_id`. Returns the balance of the account after the operation has been processed. If the specified account doesn’t exist, should return `None`.
*   `transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None` — should transfer the given amount of money from account `source_account_id` to account `target_account_id`. Returns the balance of `source_account_id` if the transfer was successful or `None` otherwise.
    *   Returns `None` if `source_account_id` or `target_account_id` doesn’t exist.
    *   Returns `None` if `source_account_id` and `target_account_id` are the same.
    *   Returns `None` if account `source_account_id` has insufficient funds to perform the transfer.

## Examples

The example below shows how these operations should work:

| Queries | Explanations |
| --- | --- |
| create\_account(1, "account1") | returns True |
| create\_account(2, "account1") | returns False; this account already exists |
| create\_account(3, "account2") | returns True |
| deposit(4, "non-existing", 2700) | returns None |
| deposit(5, "account1", 2700) | returns 2700 |
| transfer(6, "account1", "account2", 2701) | returns None; this account has insufficient funds for the transfer |
| transfer(7, "account1", "account2", 200) | returns 2500 |


## Test
You can execute a single test case by running the following command in the terminal: `pytest Questions/bank_system/test_bank_system.py::TestLevel1 -v` from the project root directory.


*   **\[execution time limit\]** 3 seconds
*   **\[memory limit\]** 1 GB

