class Account:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.balance = 0
        self.outgoing = 0  # Total outgoing transactions (transfers out, payments)
    
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
    def __init__(self):
        # Use a dictionary to store accounts: {account_id: Account}
        self.accounts: dict[str, Account] = {}

    def create_account(self, timestamp: int, account_id: str) -> bool:
        # Check if account already exists
        if account_id in self.accounts:
            return False
        # Create new account
        self.accounts[account_id] = Account(account_id)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        # Check if account exists
        if account_id not in self.accounts:
            return None
        # Add amount to balance and return new balance
        return self.accounts[account_id].deposit(amount)

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
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
        # Sort accounts by outgoing (descending), then by account_id (ascending) for ties
        sorted_accounts = sorted(
            self.accounts.keys(),
            key=lambda acc: (-self.accounts[acc].outgoing, acc)
        )
        # Take top n accounts and format the result
        return [f"{acc}({self.accounts[acc].outgoing})" for acc in sorted_accounts[:n]]

