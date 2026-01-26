## Level 4

The banking system should support merging two accounts while retaining both accounts’ balance and transaction histories.

*   `merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool` — should merge `account_id_2` into the `account_id_1`. Returns `True` if accounts were successfully merged, or `False` otherwise. Specifically:
    *   Returns `False` if `account_id_1` is equal to `account_id_2`.
    *   Returns `False` if `account_id_1` or `account_id_2` doesn’t exist.
    *   All pending cashback refunds for `account_id_2` should still be processed, but refunded to `account_id_1` instead.
    *   After the merge, it must be possible to check the status of payment transactions for `account_id_2` with payment identifiers by replacing `account_id_2` with `account_id_1`.
    *   The balance of `account_id_2` should be added to the balance of `account_id_1`.
    *   `top_spenders` operations should recognize merged accounts – the total outgoing transactions for merged accounts should be the sum of all money transferred and/or withdrawn in both accounts.
    *   `account_id_2` should be removed from the system after the merge.
*   `get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None` — should return the total amount of money in the account `account_id` at the given timestamp `time_at`. If the specified account did not exist at a given time `time_at`, returns `None`.
    *   If queries have been processed at timestamp `time_at`, `get_balance` must reflect the account balance **after** the query has been processed.
    *   If the account was merged into another account, the merged account should inherit its balance history.

## Examples

The examples below show how these operations should work:

| Queries | Explanations |
| --- | --- |
| create\_account(1, "account1") | returns True |
| create\_account(2, "account2") | returns True |
| deposit(3, "account1", 2000) | returns 2000 |
| deposit(4, "account2", 2000) | returns 2000 |
| pay(5, "account1", 500) | returns "payment1" |
| transfer(6, "account1", "account2", 500) | returns 1500 |
| merge\_accounts(7, "account1", "non-existing") | returns False; account "non-existing" does not exist |
| merge\_accounts(8, "account1", "account1") | returns False; account "account1" cannot be merged into itself |
| merge\_accounts(9, "account1", "account2") | returns True |
| get\_balance(10, "account1", 10) | returns 3000 |
| get\_balance(11, "account2", 10) | returns None; account "account2" doesn’t exist anymore |
| get\_payment\_status(12, "account1", "payment1") | returns "IN\_PROGRESS" |
| get\_payment\_status(13, "account2", "payment1") | returns None; "account2" doesn’t exist anymore |
| get\_balance(14, "account2", 1) | returns None; "account2" was not created yet |
| get\_balance(15, "account2", 9) | returns None; "account2" was already merged and doesn’t exist |
| get\_balance(16, "account1", 11) | returns 3000 |
| deposit(5 + MILLISECONDS\_IN\_1\_DAY, "account1", 100) | returns 3906 |

### Another example:

| Queries | Explanations |
| --- | --- |
| create\_account(1, "account1") | returns True |
| deposit(2, "account1", 1000) | returns 1000 |
| pay(3, "account1", 300) | returns "payment1" |
| get\_balance(4, "account1", 3) | returns 700 |
| get\_balance(5 + MILLISECONDS\_IN\_1\_DAY, "account1", 2 + MILLISECONDS\_IN\_1\_DAY) | returns 700 |
| get\_balance(6 + MILLISECONDS\_IN\_1\_DAY, "account1", 3 + MILLISECONDS\_IN\_1\_DAY) | returns 706; cashback for "payment1" was refunded |

## Test
You can execute the test cases for this level by running the following command in the terminal: `pytest Questions/bank_system/test_bank_system.py::TestLevel4 -v` from the project root directory.