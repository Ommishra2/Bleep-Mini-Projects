# Student Management System

A simple menu-driven Python project for managing student records.

## Requirements
- Python 3.10 or later
- No external libraries

## Run
```bash
python main.py
```

## Features
- Add a student
- Display all students
- Search by student ID
- Update student details
- Delete a student
- Calculate average marks
- Save and load records using `students.csv`
- Validate IDs, names, ages and marks
- Handle invalid menu choices and file errors

## OOP requirements
- **Classes and objects:** `Person`, `Student`, `CSVStorage`, `StudentManager`
- **Encapsulation:** Private attributes with properties and validation
- **Inheritance:** `Student` inherits from `Person`
- **Abstraction:** `Person` uses `abc.ABC` and `@abstractmethod`
- **File handling:** CSV data is loaded and saved using Python's `csv` module
- **Exception handling:** Invalid values, missing records and file errors are handled

## Test
Run:
```bash
python -m unittest -v
```

The tests use temporary files and do not alter the supplied `students.csv`.
