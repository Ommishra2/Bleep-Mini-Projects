# Employee Payroll System

A beginner-friendly Python OOP project that stores employee details, calculates monthly payroll, and prints payslips.

## Features
- Add and display employees
- Search by employee ID
- Calculate gross and net salary
- Generate a formatted monthly payslip
- Update and delete employee records
- Save and load records from `employees.csv`
- Validate input and handle common file/data errors

## Salary formula
- Gross salary = Basic salary + Allowance
- Net salary = Gross salary - Deduction

All amounts must be non-negative, and a deduction cannot exceed gross salary.

## OOP concepts used
- **Encapsulation:** salary fields are private and exposed through read-only properties.
- **Inheritance:** `Employee` inherits from `EmployeeBase`.
- **Abstraction:** `EmployeeBase` uses Python's `ABC` and `@abstractmethod`.
- **Composition:** `PayrollManager` uses `CSVStorage` to persist records.

## Requirements
Python 3.9 or newer. No external packages are required.

## Run
1. Open a terminal in this folder.
2. Run `python main.py`.
3. Follow the menu.

The included `employees.csv` contains sample records. You can keep it or replace it with your own data.

## Testing (optional)
Run `python -m unittest -v test_main.py` if `test_main.py` is included during development. The test file can be removed from the final submission if it is not required.
