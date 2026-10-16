# Inventory Management System

A beginner-friendly Python OOP project for managing stock and tracking inventory value.

## Features
- Add, display, search, update, and delete inventory items
- Add stock and remove stock
- Calculate stock value (quantity × unit price)
- Save and load records in `inventory.csv`
- Validate IDs, quantities, and prices; handle common errors

## OOP concepts
- **Encapsulation:** quantity and unit price use private attributes.
- **Inheritance:** `InventoryItem` inherits from `ItemBase`.
- **Abstraction:** `ItemBase` uses `ABC` and `@abstractmethod`.
- **Composition:** `InventoryManager` uses `CSVStorage`.

## Run
Requires Python 3.9 or newer. No external packages are required.
Run `python main.py` in this folder and follow the menu.
