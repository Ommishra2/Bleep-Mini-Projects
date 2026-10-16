import csv
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from pathlib import Path


def amount(value):
    try:
        value = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid number, e.g. 100 or 100.50.")
    if not value.is_finite() or value < 0:
        raise ValueError("Amount cannot be negative.")
    return value


class AccountBase(ABC):
    def __init__(self, account_id, holder):
        self.account_id = account_id
        self.holder = holder

    @property
    def account_id(self):
        return self.__account_id

    @account_id.setter
    def account_id(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Account ID cannot be empty.")
        self.__account_id = value

    @property
    def holder(self):
        return self.__holder

    @holder.setter
    def holder(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Holder name cannot be empty.")
        self.__holder = value

    @abstractmethod
    def display(self):
        pass


class BankAccount(AccountBase):
    def __init__(self, account_id, holder, balance=0):
        super().__init__(account_id, holder)
        self.balance = balance

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        self.__balance = amount(value)

    def deposit(self, value):
        value = amount(value)
        if value <= 0:
            raise ValueError("Deposit must be greater than zero.")
        self.balance += value

    def withdraw(self, value):
        value = amount(value)
        if value <= 0:
            raise ValueError("Withdrawal must be greater than zero.")
        if value > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= value

    def display(self):
        return f"ID: {self.account_id} | Holder: {self.holder} | Balance: {self.balance:.2f}"

    def to_row(self):
        return {"account_id": self.account_id, "holder": self.holder, "balance": f"{self.balance:.2f}"}

    @classmethod
    def from_row(cls, row):
        return cls(row["account_id"], row["holder"], row["balance"])


class CSVStorage:
    HEADERS = ["account_id", "holder", "balance"]

    def __init__(self, filename):
        self.filename = Path(filename)

    def load(self):
        if not self.filename.exists():
            return []
        try:
            with self.filename.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames != self.HEADERS:
                    raise ValueError("CSV headings are incorrect.")
                result = []
                for number, row in enumerate(reader, start=2):
                    try:
                        result.append(BankAccount.from_row(row))
                    except (KeyError, TypeError, ValueError) as error:
                        raise ValueError(f"Invalid data on CSV line {number}: {error}")
                return result
        except OSError as error:
            raise OSError(f"Could not read accounts file: {error}")

    def save(self, accounts):
        try:
            with self.filename.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.HEADERS)
                writer.writeheader()
                writer.writerows(account.to_row() for account in accounts)
        except OSError as error:
            raise OSError(f"Could not save accounts file: {error}")


class BankManager:
    def __init__(self, storage):
        self.storage = storage
        self.accounts = {}
        for account in storage.load():
            if account.account_id in self.accounts:
                raise ValueError(f"Duplicate ID in CSV: {account.account_id}")
            self.accounts[account.account_id] = account

    def create(self, account):
        if account.account_id in self.accounts:
            raise ValueError("Account ID already exists.")
        self.accounts[account.account_id] = account
        try:
            self.storage.save(self.accounts.values())
        except OSError:
            del self.accounts[account.account_id]
            raise

    def find(self, account_id):
        return self.accounts.get(str(account_id).strip())

    def all(self):
        return sorted(self.accounts.values(), key=lambda account: account.account_id.lower())

    def transact(self, account_id, value, operation):
        account = self.find(account_id)
        if account is None:
            raise KeyError("Account not found.")
        old_balance = account.balance
        if operation == "deposit":
            account.deposit(value)
        else:
            account.withdraw(value)
        try:
            self.storage.save(self.accounts.values())
        except OSError:
            account.balance = old_balance
            raise
        return account

    def delete(self, account_id):
        account_id = str(account_id).strip()
        if account_id not in self.accounts:
            raise KeyError("Account not found.")
        account = self.accounts.pop(account_id)
        try:
            self.storage.save(self.accounts.values())
        except OSError:
            self.accounts[account_id] = account
            raise
        return account


def main():
    try:
        bank = BankManager(CSVStorage(Path(__file__).with_name("accounts.csv")))
    except (OSError, ValueError) as error:
        print(f"Could not load accounts: {error}")
        return

    while True:
        print("--- BANK ACCOUNT MANAGEMENT ---")
        print("1. Create account")
        print("2. Display accounts")
        print("3. Check balance")
        print("4. Deposit")
        print("5. Withdraw")
        print("6. Delete account")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                bank.create(BankAccount(input("Account ID: "), input("Holder name: "),
                                        input("Opening balance (default 0): ").strip() or "0"))
                print("Account created.")
            elif choice == "2":
                accounts = bank.all()
                if not accounts:
                    print("No accounts found.")
                for account in accounts:
                    print(account.display())
            elif choice == "3":
                account = bank.find(input("Account ID: "))
                print(f"Balance: {account.balance:.2f}" if account else "Account not found.")
            elif choice in ("4", "5"):
                account_id = input("Account ID: ")
                value = input("Amount: ")
                account = bank.transact(account_id, value, "deposit" if choice == "4" else "withdraw")
                print(f"Transaction successful. New balance: {account.balance:.2f}")
            elif choice == "6":
                account = bank.delete(input("Account ID to delete: "))
                print(f"Deleted account {account.account_id}.")
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Invalid option. Choose a number from the menu.")
        except (ValueError, KeyError, OSError) as error:
            print(f"Operation failed: {error}")


if __name__ == "__main__":
    main()
