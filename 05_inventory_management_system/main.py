import csv
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

DATA_FILE = Path(__file__).with_name("inventory.csv")
MONEY_PLACES = Decimal("0.01")

def amount(value):
    try:
        result = Decimal(str(value)).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid numeric amount.")
    if not result.is_finite():
        raise ValueError("Enter a valid numeric amount.")
    return result

class ItemBase(ABC):
    def __init__(self, item_id, name):
        self.item_id = item_id.strip()
        self.name = name.strip()

    @abstractmethod
    def stock_value(self):
        pass

class InventoryItem(ItemBase):
    def __init__(self, item_id, name, quantity, unit_price):
        super().__init__(item_id, name)
        try:
            self.__quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a whole number.")
        self.__unit_price = amount(unit_price)
        self._validate()

    def _validate(self):
        if not self.item_id:
            raise ValueError("Item ID cannot be empty.")
        if not self.name:
            raise ValueError("Item name cannot be empty.")
        if self.__quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        if self.__unit_price < 0:
            raise ValueError("Unit price cannot be negative.")

    @property
    def quantity(self):
        return self.__quantity

    @property
    def unit_price(self):
        return self.__unit_price

    def stock_value(self):
        return self.__unit_price * self.__quantity

    def add_stock(self, quantity):
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a whole number.")
        if quantity <= 0:
            raise ValueError("Quantity to add must be greater than zero.")
        self.__quantity += quantity

    def remove_stock(self, quantity):
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a whole number.")
        if quantity <= 0:
            raise ValueError("Quantity to remove must be greater than zero.")
        if quantity > self.__quantity:
            raise ValueError("Not enough stock available.")
        self.__quantity -= quantity

    def to_row(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "quantity": str(self.quantity),
            "unit_price": str(self.unit_price),
        }

class CSVStorage:
    FIELDS = ["item_id", "name", "quantity", "unit_price"]

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
                return [InventoryItem(row["item_id"], row["name"],
                                      row["quantity"], row["unit_price"])
                        for row in reader]
        except (OSError, csv.Error, KeyError) as error:
            raise ValueError(f"Could not read inventory data: {error}")

    def save(self, items):
        try:
            with self.file_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDS)
                writer.writeheader()
                for item in items:
                    writer.writerow(item.to_row())
        except OSError as error:
            raise ValueError(f"Could not save inventory data: {error}")

class InventoryManager:
    def __init__(self, storage):
        self.storage = storage
        self.items = self.storage.load()
        ids = [item.item_id.casefold() for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Inventory data contains duplicate item IDs.")

    def add_item(self, item):
        if self.find_item(item.item_id):
            raise ValueError("An item with this ID already exists.")
        self.items.append(item)
        self.storage.save(self.items)

    def find_item(self, item_id):
        for item in self.items:
            if item.item_id.casefold() == item_id.strip().casefold():
                return item
        return None

    def list_items(self):
        return list(self.items)

    def update_item(self, item_id, replacement):
        old_item = self.find_item(item_id)
        if old_item is None:
            raise ValueError("Item not found.")
        if replacement.item_id.casefold() != old_item.item_id.casefold() and self.find_item(replacement.item_id):
            raise ValueError("An item with this ID already exists.")
        self.items[self.items.index(old_item)] = replacement
        self.storage.save(self.items)

    def delete_item(self, item_id):
        item = self.find_item(item_id)
        if item is None:
            raise ValueError("Item not found.")
        self.items.remove(item)
        self.storage.save(self.items)

def read_non_empty(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("This field cannot be empty.")
    return value

def read_item():
    item_id = read_non_empty("Item ID: ")
    name = read_non_empty("Item name: ")
    quantity = input("Opening quantity: ").strip()
    unit_price = input("Unit price: ").strip()
    return InventoryItem(item_id, name, quantity, unit_price)

def print_item(item):
    print(f"ID: {item.item_id} | Name: {item.name}")
    print(f"Quantity: {item.quantity}")
    print(f"Unit price: {item.unit_price:.2f}")
    print(f"Stock value: {item.stock_value():.2f}")

def show_menu():
    print("\\n===== INVENTORY MANAGEMENT SYSTEM =====")
    print("1. Add item")
    print("2. Display all items")
    print("3. Search item")
    print("4. Add stock")
    print("5. Remove stock")
    print("6. Update item details")
    print("7. Delete item")
    print("8. Exit")

def main():
    try:
        manager = InventoryManager(CSVStorage(DATA_FILE))
    except (ValueError, OSError) as error:
        print(f"Could not load inventory data: {error}")
        return
    while True:
        show_menu()
        choice = input("Choose an option (1-8): ").strip()
        try:
            if choice == "1":
                manager.add_item(read_item())
                print("Item added successfully.")
            elif choice == "2":
                items = manager.list_items()
                if not items:
                    print("No inventory items found.")
                else:
                    for item in items:
                        print_item(item)
                        print("-" * 35)
            elif choice == "3":
                item = manager.find_item(read_non_empty("Enter item ID to search: "))
                print_item(item) if item else print("Item not found.")
            elif choice in ("4", "5"):
                item_id = read_non_empty("Enter item ID: ")
                item = manager.find_item(item_id)
                if item is None:
                    print("Item not found.")
                else:
                    quantity = input("Quantity: ").strip()
                    if choice == "4":
                        item.add_stock(quantity)
                    else:
                        item.remove_stock(quantity)
                    manager.storage.save(manager.items)
                    print(f"Stock updated. New quantity: {item.quantity}")
            elif choice == "6":
                item_id = read_non_empty("Enter item ID to update: ")
                if manager.find_item(item_id) is None:
                    print("Item not found.")
                else:
                    print("Enter the item's new details.")
                    manager.update_item(item_id, read_item())
                    print("Item updated successfully.")
            elif choice == "7":
                manager.delete_item(read_non_empty("Enter item ID to delete: "))
                print("Item deleted successfully.")
            elif choice == "8":
                print("Goodbye.")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 8.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\\nInput cancelled. Exiting.")
            break

if __name__ == "__main__":
    main()
