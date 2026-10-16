import csv
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PRODUCTS_FILE = BASE_DIR / "products.csv"
ORDERS_FILE = BASE_DIR / "orders.csv"


class ShopItem(ABC):
    """Abstract base class for items sold by the shop."""

    @abstractmethod
    def get_price(self):
        pass


class Product(ShopItem):
    def __init__(self, product_id, name, price, stock):
        self.product_id = str(product_id).strip()
        self.name = str(name).strip()
        self.__price = self._valid_price(price)
        self.__stock = self._valid_stock(stock)
        if not self.product_id or not self.name:
            raise ValueError("Product ID and name cannot be empty.")

    @staticmethod
    def _valid_price(price):
        try:
            value = Decimal(str(price))
        except (InvalidOperation, ValueError):
            raise ValueError("Price must be a valid number.")
        if not value.is_finite() or value <= 0:
            raise ValueError("Price must be greater than zero.")
        return value.quantize(Decimal("0.01"))

    @staticmethod
    def _valid_stock(stock):
        try:
            value = int(stock)
        except (TypeError, ValueError):
            raise ValueError("Stock must be a whole number.")
        if str(stock).strip() != str(value) or value < 0:
            raise ValueError("Stock must be a non-negative whole number.")
        return value

    def get_price(self):
        return self.__price

    @property
    def stock(self):
        return self.__stock

    def reduce_stock(self, quantity):
        quantity = self._valid_stock(quantity)
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        if quantity > self.__stock:
            raise ValueError("Not enough stock available.")
        self.__stock -= quantity

    def to_row(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": str(self.__price),
            "stock": str(self.__stock),
        }


class Order:
    def __init__(self, order_id, items):
        self.order_id = order_id
        self.items = items  # Each item is (Product, quantity).

    @property
    def total(self):
        return sum((product.get_price() * quantity for product, quantity in self.items), Decimal("0.00"))

    def to_rows(self):
        rows = []
        for product, quantity in self.items:
            rows.append({
                "order_id": self.order_id,
                "product_id": product.product_id,
                "product_name": product.name,
                "quantity": str(quantity),
                "unit_price": str(product.get_price()),
                "line_total": str(product.get_price() * quantity),
            })
        return rows


class CSVStorage:
    PRODUCT_FIELDS = ["product_id", "name", "price", "stock"]
    ORDER_FIELDS = ["order_id", "product_id", "product_name", "quantity", "unit_price", "line_total"]

    def __init__(self, products_file=PRODUCTS_FILE, orders_file=ORDERS_FILE):
        self.products_file = Path(products_file)
        self.orders_file = Path(orders_file)
        self._ensure_file(self.products_file, self.PRODUCT_FIELDS)
        self._ensure_file(self.orders_file, self.ORDER_FIELDS)

    @staticmethod
    def _ensure_file(path, fields):
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.stat().st_size == 0:
            with path.open("w", newline="", encoding="utf-8") as file:
                csv.DictWriter(file, fieldnames=fields).writeheader()

    def load_products(self):
        products = []
        try:
            with self.products_file.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames != self.PRODUCT_FIELDS:
                    raise ValueError("Products CSV has an invalid header.")
                for row in reader:
                    products.append(Product(row["product_id"], row["name"], row["price"], row["stock"]))
        except (OSError, csv.Error, KeyError) as error:
            raise ValueError(f"Could not read products file: {error}") from error
        ids = [product.product_id for product in products]
        if len(ids) != len(set(ids)):
            raise ValueError("Products CSV contains duplicate product IDs.")
        return products

    def save_products(self, products):
        try:
            with self.products_file.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.PRODUCT_FIELDS)
                writer.writeheader()
                writer.writerows(product.to_row() for product in products)
        except OSError as error:
            raise ValueError(f"Could not save products file: {error}") from error

    def load_orders(self):
        try:
            with self.orders_file.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames != self.ORDER_FIELDS:
                    raise ValueError("Orders CSV has an invalid header.")
                return list(reader)
        except (OSError, csv.Error) as error:
            raise ValueError(f"Could not read orders file: {error}") from error

    def append_order(self, order):
        try:
            with self.orders_file.open("a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.ORDER_FIELDS)
                writer.writerows(order.to_rows())
        except OSError as error:
            raise ValueError(f"Could not save order: {error}") from error


class ShoppingManager:
    def __init__(self, storage):
        self.storage = storage
        self.products = self.storage.load_products()
        self.cart = {}  # product ID -> quantity
        self.orders = self.storage.load_orders()

    def find_product(self, product_id):
        for product in self.products:
            if product.product_id.lower() == str(product_id).strip().lower():
                return product
        return None

    def search_products(self, term):
        term = str(term).strip().lower()
        return [p for p in self.products if term in p.product_id.lower() or term in p.name.lower()]

    def add_product(self, product):
        if self.find_product(product.product_id):
            raise ValueError("A product with that ID already exists.")
        self.products.append(product)
        self.storage.save_products(self.products)

    def add_to_cart(self, product_id, quantity):
        product = self.find_product(product_id)
        if product is None:
            raise ValueError("Product not found.")
        quantity = Product._valid_stock(quantity)
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        new_quantity = self.cart.get(product.product_id, 0) + quantity
        if new_quantity > product.stock:
            raise ValueError("Requested quantity exceeds available stock.")
        self.cart[product.product_id] = new_quantity

    def cart_items(self):
        return [(self.find_product(product_id), quantity) for product_id, quantity in self.cart.items()]

    def cart_total(self):
        return sum((product.get_price() * quantity for product, quantity in self.cart_items()), Decimal("0.00"))

    def checkout(self):
        if not self.cart:
            raise ValueError("Your cart is empty.")
        items = self.cart_items()
        # Recheck stock in case it changed after items were added to the cart.
        for product, quantity in items:
            if quantity > product.stock:
                raise ValueError(f"Not enough stock for {product.name}.")
        existing_ids = [int(row["order_id"][3:]) for row in self.orders if row["order_id"].startswith("ORD") and row["order_id"][3:].isdigit()]
        order_id = f"ORD{max(existing_ids, default=0) + 1:04d}"
        order = Order(order_id, items)
        for product, quantity in items:
            product.reduce_stock(quantity)
        self.storage.save_products(self.products)
        self.storage.append_order(order)
        self.orders.extend(order.to_rows())
        self.cart.clear()
        return order

    def order_history(self):
        return self.storage.load_orders()


def display_products(products):
    if not products:
        print("No products found.")
        return
    print("\nID       Product                 Price       Stock")
    print("-" * 55)
    for product in products:
        print(f"{product.product_id:<8} {product.name:<23} ₹{product.get_price():>8.2f}   {product.stock:>5}")


def display_orders(rows):
    if not rows:
        print("No orders found.")
        return
    print("\nOrder ID   Product                 Qty   Unit Price   Line Total")
    print("-" * 68)
    for row in rows:
        print(f"{row['order_id']:<10} {row['product_name']:<23} {row['quantity']:>3}   ₹{Decimal(row['unit_price']):>8.2f}   ₹{Decimal(row['line_total']):>8.2f}")


def main():
    try:
        manager = ShoppingManager(CSVStorage())
    except (ValueError, OSError) as error:
        print(f"Could not start the shop: {error}")
        return

    while True:
        print("\n===== ONLINE SHOPPING MANAGEMENT SYSTEM =====")
        print("1. Display products")
        print("2. Search products")
        print("3. Add a product")
        print("4. Add product to cart")
        print("5. View cart")
        print("6. Checkout")
        print("7. View order history")
        print("8. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                display_products(manager.products)
            elif choice == "2":
                term = input("Enter product ID or name: ")
                display_products(manager.search_products(term))
            elif choice == "3":
                product = Product(input("Product ID: "), input("Product name: "), input("Price: "), input("Opening stock: "))
                manager.add_product(product)
                print("Product added successfully.")
            elif choice == "4":
                product_id = input("Product ID: ")
                quantity = input("Quantity: ")
                manager.add_to_cart(product_id, quantity)
                print("Product added to cart.")
            elif choice == "5":
                items = manager.cart_items()
                if not items:
                    print("Your cart is empty.")
                else:
                    display_products([product for product, _ in items])
                    for product, quantity in items:
                        print(f"{product.name}: quantity {quantity}, subtotal ₹{product.get_price() * quantity:.2f}")
                    print(f"Cart total: ₹{manager.cart_total():.2f}")
            elif choice == "6":
                order = manager.checkout()
                print(f"Order {order.order_id} placed successfully. Total: ₹{order.total:.2f}")
            elif choice == "7":
                display_orders(manager.order_history())
            elif choice == "8":
                print("Thank you for shopping. Goodbye!")
                break
            else:
                print("Invalid option. Please choose 1 to 8.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
