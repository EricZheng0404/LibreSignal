from collections import deque
class Account:
    def __init__(self, account_id: str, created_at: int):
        self.account_id = account_id
        self.balance = 0
        self.outgoing = 0  # Total outgoing transactions (transfers out, payments)
        self.payments: dict[str, str] = {}  # {payment_id: status}
        self.created_at = created_at
        # Balance history: list of (timestamp, balance) - records balance AFTER each operation
        self.balance_history: list[tuple[int, int]] = [(created_at, 0)]
    
    def record_balance(self, timestamp: int) -> None:
        """Record current balance at this timestamp."""
        self.balance_history.append((timestamp, self.balance))
    
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
    
    def get_balance_at(self, time_at: int) -> int | None:
        """Get balance at a specific timestamp. Returns None if account didn't exist."""
        if time_at < self.created_at:
            return None
        # Find the latest balance at or before time_at
        result = None
        for ts, balance in self.balance_history:
            if ts <= time_at:
                result = balance
            else:
                break
        return result


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
        self.accounts[account_id] = Account(account_id, timestamp)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._process_cashbacks(timestamp)
        # Check if account exists
        if account_id not in self.accounts:
            return None
        # Add amount to balance and return new balance
        account = self.accounts[account_id]
        result = account.deposit(amount)
        account.record_balance(timestamp)
        return result

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
        # Record balance history for both accounts
        source.record_balance(timestamp)
        target.record_balance(timestamp)
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
            cb_timestamp, account_id, amount, payment_id = self.pending_cashbacks.popleft()
            if account_id in self.accounts:
                account = self.accounts[account_id]
                account.deposit(amount)
                account.payments[payment_id] = "CASHBACK_RECEIVED"
                account.record_balance(cb_timestamp)

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
        
        # Record balance after payment
        account.record_balance(timestamp)

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
    
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        self._process_cashbacks(timestamp)
        # Check if both accounts are different
        if account_id_1 == account_id_2:
            return False
        # Check if both accounts exist
        if account_id_1 not in self.accounts or account_id_2 not in self.accounts:
            return False
        
        account1 = self.accounts[account_id_1]
        account2 = self.accounts[account_id_2]
        
        # Merge balance
        account1.balance += account2.balance
        
        # Merge outgoing transactions
        account1.outgoing += account2.outgoing
        
        # Merge payments (account1 inherits account2's payment statuses)
        account1.payments.update(account2.payments)
        
        # Merge balance history - combine and sort by timestamp
        account1.balance_history.extend(account2.balance_history)
        account1.balance_history.sort(key=lambda x: x[0])
        
        # Update created_at to the earlier of the two
        account1.created_at = min(account1.created_at, account2.created_at)
        
        # Record the merged balance
        account1.record_balance(timestamp)
        
        # Redirect pending cashbacks from account2 to account1
        for i, (cb_ts, acc_id, amount, payment_id) in enumerate(self.pending_cashbacks):
            if acc_id == account_id_2:
                self.pending_cashbacks[i] = (cb_ts, account_id_1, amount, payment_id)
        
        # Remove account2 from the system
        del self.accounts[account_id_2]
        
        return True
    
    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        self._process_cashbacks(timestamp)
        # Check if account exists
        if account_id not in self.accounts:
            return None
        
        account = self.accounts[account_id]
        return account.get_balance_at(time_at)