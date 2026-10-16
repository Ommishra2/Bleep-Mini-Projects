"""Simple Library Management System using OOP and CSV storage."""
import csv
from abc import ABC, abstractmethod
from pathlib import Path


class LibraryItem(ABC):
    """Abstract base class for a library item."""

    def __init__(self, item_id, title):
        self.__item_id = ""
        self.__title = ""
        self.item_id = item_id
        self.title = title

    @property
    def item_id(self):
        return self.__item_id

    @item_id.setter
    def item_id(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Book ID cannot be empty.")
        self.__item_id = value

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Title cannot be empty.")
        self.__title = value

    @abstractmethod
    def display(self):
        pass


class Book(LibraryItem):
    """Book record with author and availability."""

    def __init__(self, book_id, title, author, available=True):
        super().__init__(book_id, title)
        self.author = author
        self.available = available

    @property
    def author(self):
        return self.__author

    @author.setter
    def author(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Author cannot be empty.")
        self.__author = value

    @property
    def available(self):
        return self.__available

    @available.setter
    def available(self, value):
        if isinstance(value, bool):
            self.__available = value
        elif str(value).strip().lower() in ("yes", "true", "1"):
            self.__available = True
        elif str(value).strip().lower() in ("no", "false", "0"):
            self.__available = False
        else:
            raise ValueError("Availability must be yes or no.")

    def display(self):
        status = "Available" if self.available else "Issued"
        return f"ID: {self.item_id} | Title: {self.title} | Author: {self.author} | Status: {status}"

    def to_row(self):
        return {
            "book_id": self.item_id,
            "title": self.title,
            "author": self.author,
            "available": "yes" if self.available else "no",
        }

    @classmethod
    def from_row(cls, row):
        return cls(row["book_id"], row["title"], row["author"], row["available"])


class CSVStorage:
    HEADERS = ["book_id", "title", "author", "available"]

    def __init__(self, filename):
        self.filename = Path(filename)

    def load(self):
        if not self.filename.exists():
            return []
        try:
            with self.filename.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames != self.HEADERS:
                    raise ValueError("CSV file has incorrect column headings.")
                books = []
                for line_number, row in enumerate(reader, start=2):
                    try:
                        books.append(Book.from_row(row))
                    except (KeyError, TypeError, ValueError) as error:
                        raise ValueError(f"Invalid book data on line {line_number}: {error}")
                return books
        except OSError as error:
            raise OSError(f"Could not read books file: {error}")

    def save(self, books):
        try:
            with self.filename.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.HEADERS)
                writer.writeheader()
                for book in books:
                    writer.writerow(book.to_row())
        except OSError as error:
            raise OSError(f"Could not save books file: {error}")


class LibraryManager:
    def __init__(self, storage):
        self.storage = storage
        self.books = {}
        for book in storage.load():
            if book.item_id in self.books:
                raise ValueError(f"Duplicate book ID in CSV: {book.item_id}")
            self.books[book.item_id] = book

    def add_book(self, book):
        if book.item_id in self.books:
            raise ValueError("That book ID already exists.")
        self.books[book.item_id] = book
        try:
            self.storage.save(self.books.values())
        except OSError:
            del self.books[book.item_id]
            raise

    def all_books(self):
        return sorted(self.books.values(), key=lambda book: book.item_id.lower())

    def available_books(self):
        return [book for book in self.all_books() if book.available]

    def search(self, book_id):
        return self.books.get(str(book_id).strip())

    def search_title_or_author(self, text):
        text = str(text).strip().lower()
        return [
            book for book in self.all_books()
            if text in book.title.lower() or text in book.author.lower()
        ]

    def issue_book(self, book_id):
        book = self.search(book_id)
        if book is None:
            raise KeyError("Book not found.")
        if not book.available:
            raise ValueError("That book is already issued.")
        book.available = False
        try:
            self.storage.save(self.books.values())
        except OSError:
            book.available = True
            raise
        return book

    def return_book(self, book_id):
        book = self.search(book_id)
        if book is None:
            raise KeyError("Book not found.")
        if book.available:
            raise ValueError("That book is already marked available.")
        book.available = True
        try:
            self.storage.save(self.books.values())
        except OSError:
            book.available = False
            raise
        return book

    def delete_book(self, book_id):
        book_id = str(book_id).strip()
        if book_id not in self.books:
            raise KeyError("Book not found.")
        book = self.books.pop(book_id)
        try:
            self.storage.save(self.books.values())
        except OSError:
            self.books[book_id] = book
            raise
        return book


def main():
    data_file = Path(__file__).with_name("books.csv")
    try:
        library = LibraryManager(CSVStorage(data_file))
    except (OSError, ValueError) as error:
        print(f"Could not load books: {error}")
        return

    while True:
        print("\n--- LIBRARY MANAGEMENT SYSTEM ---")
        print("1. Add book")
        print("2. Display all books")
        print("3. Search by ID, title or author")
        print("4. Display available books")
        print("5. Issue book")
        print("6. Return book")
        print("7. Delete book")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                book_id = input("Book ID: ").strip()
                title = input("Title: ").strip()
                author = input("Author: ").strip()
                library.add_book(Book(book_id, title, author))
                print("Book added successfully.")
            elif choice == "2":
                books = library.all_books()
                if not books:
                    print("No books found.")
                for book in books:
                    print(book.display())
            elif choice == "3":
                term = input("Enter book ID, title or author: ").strip()
                book = library.search(term)
                matches = [book] if book else library.search_title_or_author(term)
                if matches:
                    for item in matches:
                        print(item.display())
                else:
                    print("No matching books found.")
            elif choice == "4":
                books = library.available_books()
                if not books:
                    print("No books are currently available.")
                for book in books:
                    print(book.display())
            elif choice == "5":
                book = library.issue_book(input("Book ID to issue: "))
                print("Book issued:", book.display())
            elif choice == "6":
                book = library.return_book(input("Book ID to return: "))
                print("Book returned:", book.display())
            elif choice == "7":
                book = library.delete_book(input("Book ID to delete: "))
                print(f"Deleted: {book.title}")
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Choose one of the listed menu options.")
        except (ValueError, KeyError, OSError) as error:
            print(f"Operation failed: {error}")


if __name__ == "__main__":
    main()
