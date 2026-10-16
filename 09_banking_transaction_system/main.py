import csv
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

DATA_FILE = Path(__file__).with_name("transactions.csv")
MONEY_PLACES = Decimal("0.01")


def money(value):
    try:
        result = Decimal(str(value)).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid monetary amount.")
    if not result.is_finite():
        raise ValueError("Enter a valid monetary amount.")
    return result


class TransactionBase(ABC):
    """Abstract base class for bank transactions."""

    def __init__(self, transaction_id, account_id, transaction_type, amount):
        self.transaction_id = transaction_id.strip()
        self.account_id = account_id.strip()
        self.transaction_type = transaction_type.strip().title()
        self.amount = money(amount)

    @abstractmethod
    def summary(self):
        pass


class BankTransaction(TransactionBase):
    """Represents a deposit or withdrawal transaction."""

    def __init__(self, transaction_id, account_id, transaction_type, amount, note=""):
        super().__init__(transaction_id, account_id, transaction_type, amount)
        self.note = note.strip()
        self._validate()

    def _validate(self):
        if not self.transaction_id:
            raise ValueError("Transaction ID cannot be empty.")
        if not self.account_id:
            raise ValueError("Account ID cannot be empty.")
        if self.transaction_type not in ("Deposit", "Withdrawal"):
            raise ValueError("Transaction type must be Deposit or Withdrawal.")
        if self.amount <= 0:
            raise ValueError("Transaction amount must be greater than zero.")

    def summary(self):
        return (
            f"Transaction ID: {self.transaction_id} | "
            f"Account ID: {self.account_id} | "
            f"Type: {self.transaction_type} | "
            f"Amount: {self.amount:.2f} | Note: {self.note or '-'}"
        )

    def to_row(self):
        return {
            "transaction_id": self.transaction_id,
            "account_id": self.account_id,
            "transaction_type": self.transaction_type,
            "amount": str(self.amount),
            "note": self.note,
        }


class CSVStorage:
    FIELDS = ["transaction_id", "account_id", "transaction_type", "amount", "note"]

    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def load(self):
        if not self.file_path.exists():
            return []
        try:
            with self.file_path.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames != self.FIELDS:
                    raise ValueError("CSV file has an invalid header.")
                return [
                    BankTransaction(row["transaction_id"], row["account_id"],
                                    row["transaction_type"], row["amount"], row["note"])
                    for row in reader
                ]
        except (OSError, csv.Error, KeyError) as error:
            raise ValueError(f"Could not read transactions: {error}")

    def save(self, transactions):
        try:
            with self.file_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDS)
                writer.writeheader()
                for transaction in transactions:
                    writer.writerow(transaction.to_row())
        except OSError as error:
            raise ValueError(f"Could not save transactions: {error}")


class TransactionManager:
    """Records and searches transactions for account IDs."""

    def __init__(self, storage):
        self.storage = storage
        self.transactions = self.storage.load()
        ids = [item.transaction_id.casefold() for item in self.transactions]
        if len(ids) != len(set(ids)):
            raise ValueError("Transaction data contains duplicate transaction IDs.")

    def record_transaction(self, transaction):
        if self.find_transaction(transaction.transaction_id):
            raise ValueError("A transaction with this ID already exists.")
        self.transactions.append(transaction)
        self.storage.save(self.transactions)

    def find_transaction(self, transaction_id):
        for transaction in self.transactions:
            if transaction.transaction_id.casefold() == transaction_id.strip().casefold():
                return transaction
        return None

    def list_transactions(self):
        return list(self.transactions)

    def account_transactions(self, account_id):
        return [item for item in self.transactions
                if item.account_id.casefold() == account_id.strip().casefold()]

    def account_totals(self, account_id):
        deposits = sum(
            (item.amount for item in self.account_transactions(account_id)
             if item.transaction_type == "Deposit"), Decimal("0.00")
        )
        withdrawals = sum(
            (item.amount for item in self.account_transactions(account_id)
             if item.transaction_type == "Withdrawal"), Decimal("0.00")
        )
        return deposits, withdrawals, deposits - withdrawals


def read_non_empty(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("This field cannot be empty.")
    return value


def read_transaction():
    transaction_id = read_non_empty("Transaction ID: ")
    account_id = read_non_empty("Account ID: ")
    transaction_type = read_non_empty("Type (Deposit/Withdrawal): ")
    amount_value = input("Amount: ").strip()
    note = input("Note (optional): ").strip()
    return BankTransaction(transaction_id, account_id, transaction_type, amount_value, note)


def show_menu():
    print("\n===== BANKING TRANSACTION SYSTEM =====")
    print("1. Record transaction")
    print("2. Display all transactions")
    print("3. Search transaction by ID")
    print("4. View transactions for an account")
    print("5. Show account totals")
    print("6. Exit")


def main():
    try:
        manager = TransactionManager(CSVStorage(DATA_FILE))
    except (ValueError, OSError) as error:
        print(f"Could not load transaction data: {error}")
        return

    while True:
        show_menu()
        choice = input("Choose an option (1-6): ").strip()
        try:
            if choice == "1":
                manager.record_transaction(read_transaction())
                print("Transaction recorded successfully.")
            elif choice == "2":
                transactions = manager.list_transactions()
                if not transactions:
                    print("No transactions found.")
                else:
                    for transaction in transactions:
                        print(transaction.summary())
            elif choice == "3":
                transaction = manager.find_transaction(
                    read_non_empty("Enter transaction ID: "))
                if transaction:
                    print(transaction.summary())
                else:
                    print("Transaction not found.")
            elif choice == "4":
                account_id = read_non_empty("Enter account ID: ")
                transactions = manager.account_transactions(account_id)
                if not transactions:
                    print("No transactions found for this account.")
                else:
                    for transaction in transactions:
                        print(transaction.summary())
            elif choice == "5":
                account_id = read_non_empty("Enter account ID: ")
                deposits, withdrawals, balance = manager.account_totals(account_id)
                print(f"Total deposits: {deposits:.2f}")
                print(f"Total withdrawals: {withdrawals:.2f}")
                print(f"Net transaction total: {balance:.2f}")
                print("Note: This is calculated from recorded transactions only, not a bank account balance.")
            elif choice == "6":
                print("Goodbye.")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 6.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled. Exiting.")
            break


if __name__ == "__main__":
    main()
