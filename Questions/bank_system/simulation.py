"""
All your implementation code for the bank system simulation goes here.
"""

class Simulation:

    def __init__(self):
        pass

    def create_account(self, timestamp: int, account_id: str) -> bool | None:
        pass

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        pass

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        pass

    def top_spenders(self, timestamp: int, n: int) -> list[str] | None:
        pass

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        pass

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        pass

    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool | None:
        pass

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        pass
