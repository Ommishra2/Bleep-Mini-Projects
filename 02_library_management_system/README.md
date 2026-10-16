# Library Management System

A beginner-friendly console application for managing a small library.

## Run
Requires Python 3.10 or later. No external packages are needed.

```bash
python main.py
```

## Features
1. Add a book
2. Display all books
3. Search by ID, title, or author
4. Display available books
5. Issue a book
6. Return a book
7. Delete a book
8. Save/load records using `books.csv`
9. Reject duplicate IDs and invalid fields
10. Handle invalid menu choices and file errors

## OOP concepts
- **Classes and objects:** `LibraryItem`, `Book`, `CSVStorage`, `LibraryManager`
- **Encapsulation:** private attributes with properties and validation
- **Inheritance:** `Book` inherits from `LibraryItem`
- **Abstraction:** `LibraryItem` uses `abc.ABC` and `@abstractmethod`
- **File handling:** CSV records are loaded and saved with Python's `csv` module
- **Exception handling:** invalid values, duplicate IDs, missing books and file errors are handled

## Tests
Run:
```bash
python -m unittest -v
```

The tests use temporary files and do not modify the supplied `books.csv`.
