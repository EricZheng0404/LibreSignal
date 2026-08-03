"""
Reference solution for the bank system simulation problem.

It covers account creation, deposits, transfers, top spenders, payments with
cashback, account merging, and historical balance lookup.
"""

from __future__ import annotations

from collections import deque


class Account:
    def __init__(self, account_id: str, created_at: int):
        self.account_id = account_id
        self.balance = 0
        self.outgoing = 0
        self.payments: dict[str, str] = {}
        self.created_at = created_at
        self.removed_at: int | None = None
        self.balance_history: list[tuple[int, int]] = [(created_at, 0)]

    def exists_at(self, timestamp: int) -> bool:
        if timestamp < self.created_at:
            return False
        return self.removed_at is None or timestamp < self.removed_at

    def record_balance(self, timestamp: int) -> None:
        self.balance_history.append((timestamp, self.balance))

    def deposit(self, amount: int) -> int:
        self.balance += amount
        return self.balance

    def withdraw(self, amount: int) -> bool:
        if self.balance < amount:
            return False
        self.balance -= amount
        self.outgoing += amount
        return True

    def get_balance_at(self, timestamp: int) -> int | None:
        if not self.exists_at(timestamp):
            return None

        result = None
        for event_timestamp, balance in self.balance_history:
            if event_timestamp <= timestamp:
                result = balance
            else:
                break
        return result


class Simulation:
    CASHBACK_DELAY = 24 * 60 * 60 * 1000

    def __init__(self):
        self.accounts: dict[str, Account] = {}
        self.archived_accounts: dict[str, list[Account]] = {}
        self.payment_counter = 0
        self.pending_cashbacks: deque[tuple[int, str, int, str]] = deque()

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._process_cashbacks(timestamp)
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = Account(account_id, timestamp)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._process_cashbacks(timestamp)
        account = self.accounts.get(account_id)
        if account is None:
            return None

        result = account.deposit(amount)
        account.record_balance(timestamp)
        return result

    def transfer(
        self,
        timestamp: int,
        source_account_id: str,
        target_account_id: str,
        amount: int,
    ) -> int | None:
        self._process_cashbacks(timestamp)
        if source_account_id == target_account_id:
            return None

        source = self.accounts.get(source_account_id)
        target = self.accounts.get(target_account_id)
        if source is None or target is None:
            return None
        if not source.withdraw(amount):
            return None

        target.deposit(amount)
        source.record_balance(timestamp)
        target.record_balance(timestamp)
        return source.balance

    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        self._process_cashbacks(timestamp)
        sorted_accounts = sorted(
            self.accounts.values(),
            key=lambda account: (-account.outgoing, account.account_id),
        )
        return [
            f"{account.account_id}({account.outgoing})"
            for account in sorted_accounts[:n]
        ]

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        self._process_cashbacks(timestamp)
        account = self.accounts.get(account_id)
        if account is None or not account.withdraw(amount):
            return None

        self.payment_counter += 1
        payment_id = f"payment{self.payment_counter}"
        account.payments[payment_id] = "IN_PROGRESS"
        account.record_balance(timestamp)

        cashback_amount = amount * 2 // 100
        cashback_timestamp = timestamp + self.CASHBACK_DELAY
        self.pending_cashbacks.append(
            (cashback_timestamp, account_id, cashback_amount, payment_id)
        )
        return payment_id

    def get_payment_status(
        self,
        timestamp: int,
        account_id: str,
        payment: str,
    ) -> str | None:
        self._process_cashbacks(timestamp)
        account = self.accounts.get(account_id)
        if account is None:
            return None
        return account.payments.get(payment)

    def merge_accounts(
        self,
        timestamp: int,
        account_id_1: str,
        account_id_2: str,
    ) -> bool:
        self._process_cashbacks(timestamp)
        if account_id_1 == account_id_2:
            return False

        account1 = self.accounts.get(account_id_1)
        account2 = self.accounts.get(account_id_2)
        if account1 is None or account2 is None:
            return False

        account1.balance += account2.balance
        account1.outgoing += account2.outgoing
        account1.payments.update(account2.payments)
        account1.record_balance(timestamp)

        for index, (cb_ts, acc_id, amount, payment_id) in enumerate(
            self.pending_cashbacks
        ):
            if acc_id == account_id_2:
                self.pending_cashbacks[index] = (
                    cb_ts,
                    account_id_1,
                    amount,
                    payment_id,
                )

        account2.removed_at = timestamp
        self.archived_accounts.setdefault(account_id_2, []).append(account2)
        del self.accounts[account_id_2]
        return True

    def get_balance(
        self,
        timestamp: int,
        account_id: str,
        time_at: int,
    ) -> int | None:
        self._process_cashbacks(timestamp)
        account = self._find_account_version(account_id, time_at)
        if account is None:
            return None
        return account.get_balance_at(time_at)

    def _process_cashbacks(self, timestamp: int) -> None:
        while self.pending_cashbacks and self.pending_cashbacks[0][0] <= timestamp:
            cb_timestamp, account_id, amount, payment_id = (
                self.pending_cashbacks.popleft()
            )
            account = self.accounts.get(account_id)
            if account is None:
                continue

            account.deposit(amount)
            account.payments[payment_id] = "CASHBACK_RECEIVED"
            account.record_balance(cb_timestamp)

    def _find_account_version(
        self,
        account_id: str,
        timestamp: int,
    ) -> Account | None:
        account = self.accounts.get(account_id)
        if account is not None and account.exists_at(timestamp):
            return account

        for archived_account in reversed(self.archived_accounts.get(account_id, [])):
            if archived_account.exists_at(timestamp):
                return archived_account
        return None
