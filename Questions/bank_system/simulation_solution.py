from collections import deque
class Account:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.balance = 0
        self.outgoing = 0  # Total outgoing transactions (transfers out, payments)
        self.payments: dict[str, str] = {}  # {payment_id: status}
    
    def deposit(self, amount: int) -> int:
        self.balance += amount
        return self.balance
    
    def withdraw(self, amount: int) -> bool:
        """Withdraw amount if sufficient funds. Returns True if successful."""
        if self.balance < amount:
            return False
        self.balance -= amount
        self.outgoing += amount
        return True


class Simulation:
    CASHBACK_DELAY = 24 * 60 * 60 * 1000  # 24 hours in milliseconds

    def __init__(self):
        # Use a dictionary to store accounts: {account_id: Account}
        self.accounts: dict[str, Account] = {}
        self.payment_counter = 0  # Global counter for payment IDs
        # Pending cashbacks: list of (timestamp, account_id, amount, payment_id)
        self.pending_cashbacks: deque[tuple[int, str, int, str]] = deque()

    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._process_cashbacks(timestamp)
        # Check if account already exists
        if account_id in self.accounts:
            return False
        # Create new account
        self.accounts[account_id] = Account(account_id)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._process_cashbacks(timestamp)
        # Check if account exists
        if account_id not in self.accounts:
            return None
        # Add amount to balance and return new balance
        return self.accounts[account_id].deposit(amount)

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        self._process_cashbacks(timestamp)
        # Check if both accounts exist
        if source_account_id not in self.accounts or target_account_id not in self.accounts:
            return None
        # Check if source and target are the same
        if source_account_id == target_account_id:
            return None
        
        source = self.accounts[source_account_id]
        target = self.accounts[target_account_id]
        
        # Check if source has sufficient funds and perform withdrawal
        if not source.withdraw(amount):
            return None
        
        # Deposit to target
        target.deposit(amount)
        return source.balance
    
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        self._process_cashbacks(timestamp)
        # Sort accounts by outgoing (descending), then by account_id (ascending) for ties
        sorted_accounts = sorted(
            self.accounts.keys(),
            key=lambda acc: (-self.accounts[acc].outgoing, acc)
        )
        # Take top n accounts and format the result
        return [f"{acc}({self.accounts[acc].outgoing})" for acc in sorted_accounts[:n]]

    def _process_cashbacks(self, timestamp: int) -> None:
        """Process all cashbacks that are due at or before the given timestamp."""
        while self.pending_cashbacks and self.pending_cashbacks[0][0] <= timestamp:
            _, account_id, amount, payment_id = self.pending_cashbacks.popleft()
            if account_id in self.accounts:
                self.accounts[account_id].deposit(amount)
                self.accounts[account_id].payments[payment_id] = "CASHBACK_RECEIVED"

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        self._process_cashbacks(timestamp)
        # Check if account exists
        if account_id not in self.accounts:
            return None
        
        account = self.accounts[account_id]
        
        # Check if account has sufficient funds
        # Outgoing is accounted in withdraw method
        if not account.withdraw(amount):
            return None
        
        # Generate payment ID
        self.payment_counter += 1
        payment_id = f"payment{self.payment_counter}"
        
        # Store payment status
        account.payments[payment_id] = "IN_PROGRESS"

        # Schedule cashback (2% rounded down) for 24 hours later
        cashback_amount = amount * 2 // 100
        cashback_timestamp = timestamp + self.CASHBACK_DELAY
        self.pending_cashbacks.append((cashback_timestamp, account_id, cashback_amount, payment_id))
        
        return payment_id

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        self._process_cashbacks(timestamp)
        # Check if account exists
        if account_id not in self.accounts:
            return None
        
        account = self.accounts[account_id]
        
        # Check if payment exists for this account
        if payment not in account.payments:
            return None
        
        return account.payments[payment]
    