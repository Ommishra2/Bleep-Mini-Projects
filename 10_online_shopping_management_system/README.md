# Online Shopping Management System

A beginner-friendly Python OOP console project that demonstrates a simple online shop using CSV files.

## Features
- Display and search products by ID or name
- Add products to the product list
- Add products and quantities to a shopping cart
- View cart subtotals and the total price
- Checkout, reduce stock, and save order details
- View order history
- Validate prices, quantities, stock, and duplicate product IDs
- Handle common input and file errors

## OOP concepts demonstrated
- **Abstraction:** `ShopItem` is an abstract base class using `abc.ABC` and `@abstractmethod`.
- **Inheritance:** `Product` inherits from `ShopItem`.
- **Encapsulation:** product price and stock are private attributes; stock changes through a method.
- **Classes and objects:** `Product`, `Order`, `CSVStorage`, and `ShoppingManager` have separate responsibilities.
- **File handling:** products are stored in `products.csv`; order lines are stored in `orders.csv`.
- **Exception handling:** invalid values and common file errors are handled with clear messages.

## Requirements
- Python 3.9 or later
- No third-party packages required

## Run
Open a terminal in this folder and run:

```bash
python main.py
```

The sample product list is included. New products, stock changes, and order history are saved to the CSV files. This is an educational project, not a real payment system; it does not process payments or store customer payment information.
