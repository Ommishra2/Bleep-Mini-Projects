"""Simple Student Management System for an introductory Python OOP assignment."""
import csv
from abc import ABC, abstractmethod
from pathlib import Path


class Person(ABC):
    """Abstract base class."""

    def __init__(self, person_id, name, age):
        self.__person_id = ""
        self.__name = ""
        self.__age = 0
        self.person_id = person_id
        self.name = name
        self.age = age

    @property
    def person_id(self):
        return self.__person_id

    @person_id.setter
    def person_id(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Student ID cannot be empty.")
        self.__person_id = value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Name cannot be empty.")
        self.__name = value

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Age must be a whole number.")
        if value < 1 or value > 120:
            raise ValueError("Age must be between 1 and 120.")
        self.__age = value

    @abstractmethod
    def display(self):
        pass


class Student(Person):
    """Student is a Person with marks."""

    def __init__(self, student_id, name, age, marks):
        super().__init__(student_id, name, age)
        self.marks = marks

    @property
    def marks(self):
        return self.__marks[:]

    @marks.setter
    def marks(self, values):
        try:
            values = [float(value) for value in values]
        except (TypeError, ValueError):
            raise ValueError("Marks must be numbers.")
        if len(values) == 0:
            raise ValueError("Enter at least one mark.")
        if any(value < 0 or value > 100 for value in values):
            raise ValueError("Every mark must be between 0 and 100.")
        self.__marks = values

    @property
    def average(self):
        return sum(self.__marks) / len(self.__marks)

    def display(self):
        marks_text = ", ".join(str(mark) for mark in self.__marks)
        return (f"ID: {self.person_id} | Name: {self.name} | Age: {self.age} | "
                f"Marks: {marks_text} | Average: {self.average:.2f}")

    def to_row(self):
        return {
            "student_id": self.person_id,
            "name": self.name,
            "age": self.age,
            "marks": ";".join(str(mark) for mark in self.__marks)
        }

    @classmethod
    def from_row(cls, row):
        marks = row["marks"].split(";")
        return cls(row["student_id"], row["name"], row["age"], marks)


class CSVStorage:
    """Reads and writes student records."""

    HEADERS = ["student_id", "name", "age", "marks"]

    def __init__(self, filename):
        self.filename = Path(filename)

    def load(self):
        if not self.filename.exists():
            return []
        students = []
        try:
            with self.filename.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames != self.HEADERS:
                    raise ValueError("CSV file has incorrect column headings.")
                for row in reader:
                    students.append(Student.from_row(row))
        except OSError as error:
            raise OSError(f"Could not read data file: {error}")
        except (KeyError, TypeError) as error:
            raise ValueError(f"Invalid row in CSV file: {error}")
        return students

    def save(self, students):
        try:
            with self.filename.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.HEADERS)
                writer.writeheader()
                for student in students:
                    writer.writerow(student.to_row())
        except OSError as error:
            raise OSError(f"Could not save data file: {error}")


class StudentManager:
    """Provides student add, search, update, delete and display operations."""

    def __init__(self, storage):
        self.storage = storage
        self.students = {}
        for student in self.storage.load():
            if student.person_id in self.students:
                raise ValueError("Duplicate student ID found in CSV.")
            self.students[student.person_id] = student

    def add(self, student):
        if student.person_id in self.students:
            raise ValueError("That student ID already exists.")
        self.students[student.person_id] = student
        try:
            self.storage.save(self.students.values())
        except OSError:
            del self.students[student.person_id]
            raise

    def all_students(self):
        return sorted(self.students.values(), key=lambda student: student.person_id.lower())

    def search(self, student_id):
        return self.students.get(str(student_id).strip())

    def update(self, student_id, name, age, marks):
        old = self.search(student_id)
        if old is None:
            raise KeyError("Student not found.")
        # Build and validate a replacement before changing the stored record.
        updated = Student(
            old.person_id,
            old.name if name == "" else name,
            old.age if age == "" else age,
            old.marks if marks == "" else marks.split(",")
        )
        self.students[old.person_id] = updated
        try:
            self.storage.save(self.students.values())
        except OSError:
            self.students[old.person_id] = old
            raise
        return updated

    def delete(self, student_id):
        student_id = str(student_id).strip()
        if student_id not in self.students:
            raise KeyError("Student not found.")
        deleted = self.students.pop(student_id)
        try:
            self.storage.save(self.students.values())
        except OSError:
            self.students[student_id] = deleted
            raise
        return deleted


def read_age():
    while True:
        try:
            age = input("Age: ").strip()
            age = int(age)
            if not 1 <= age <= 120:
                raise ValueError
            return age
        except ValueError:
            print("Enter a whole number from 1 to 120.")


def read_marks():
    while True:
        try:
            raw = input("Marks separated by commas (example 70,80,90): ")
            marks = [float(part.strip()) for part in raw.split(",") if part.strip()]
            if not marks or any(mark < 0 or mark > 100 for mark in marks):
                raise ValueError
            return marks
        except ValueError:
            print("Enter one or more marks from 0 to 100, separated by commas.")


def main():
    data_file = Path(__file__).with_name("students.csv")
    try:
        manager = StudentManager(CSVStorage(data_file))
    except (OSError, ValueError) as error:
        print(f"Could not load student records: {error}")
        return

    while True:
        print("\n--- STUDENT MANAGEMENT SYSTEM ---")
        print("1. Add student")
        print("2. Display all students")
        print("3. Search student")
        print("4. Update student")
        print("5. Delete student")
        print("6. Calculate average")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                student_id = input("Student ID: ").strip()
                name = input("Name: ").strip()
                age = read_age()
                marks = read_marks()
                manager.add(Student(student_id, name, age, marks))
                print("Student added successfully.")
            elif choice == "2":
                students = manager.all_students()
                if not students:
                    print("No students found.")
                for student in students:
                    print(student.display())
            elif choice == "3":
                student = manager.search(input("Student ID: "))
                print(student.display() if student else "Student not found.")
            elif choice == "4":
                student_id = input("Student ID to update: ").strip()
                if manager.search(student_id) is None:
                    print("Student not found.")
                    continue
                print("Press Enter to keep an existing value.")
                name = input("New name: ").strip()
                age = input("New age: ").strip()
                marks = input("New marks, separated by commas: ").strip()
                manager.update(student_id, name, age, marks)
                print("Student updated successfully.")
            elif choice == "5":
                student = manager.delete(input("Student ID to delete: "))
                print(f"Deleted {student.name}.")
            elif choice == "6":
                student = manager.search(input("Student ID: "))
                if student:
                    print(f"{student.name}'s average is {student.average:.2f}.")
                else:
                    print("Student not found.")
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Choose one of the listed menu options.")
        except (ValueError, KeyError, OSError) as error:
            print(f"Operation failed: {error}")


if __name__ == "__main__":
    main()
