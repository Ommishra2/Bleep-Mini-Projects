import csv
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


DATA_FILE = Path(__file__).with_name("employees.csv")
MONEY_PLACES = Decimal("0.01")


def money(value):
    """Convert a value to a two-decimal-place amount."""
    try:
        amount = Decimal(str(value)).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid amount.")
    if not amount.is_finite():
        raise ValueError("Enter a valid amount.")
    return amount


class EmployeeBase(ABC):
    """Abstract base class for employee records."""

    def __init__(self, employee_id, name):
        self.employee_id = employee_id.strip()
        self.name = name.strip()

    @abstractmethod
    def calculate_pay(self):
        """Return the employee's net pay."""
        pass


class Employee(EmployeeBase):
    """Stores employee details and calculates monthly pay."""

    def __init__(self, employee_id, name, basic_salary, allowance, deduction):
        super().__init__(employee_id, name)
        self.__basic_salary = money(basic_salary)
        self.__allowance = money(allowance)
        self.__deduction = money(deduction)
        self._validate()

    def _validate(self):
        if not self.employee_id:
            raise ValueError("Employee ID cannot be empty.")
        if not self.name:
            raise ValueError("Employee name cannot be empty.")
        if min(self.__basic_salary, self.__allowance, self.__deduction) < 0:
            raise ValueError("Salary, allowance, and deduction cannot be negative.")
        if self.__deduction > self.gross_salary:
            raise ValueError("Deduction cannot exceed gross salary.")

    @property
    def basic_salary(self):
        return self.__basic_salary

    @property
    def allowance(self):
        return self.__allowance

    @property
    def deduction(self):
        return self.__deduction

    @property
    def gross_salary(self):
        return self.__basic_salary + self.__allowance

    def calculate_pay(self):
        return self.gross_salary - self.__deduction

    def to_row(self):
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "basic_salary": str(self.basic_salary),
            "allowance": str(self.allowance),
            "deduction": str(self.deduction),
        }


class CSVStorage:
    """Reads and writes employee records in a CSV file."""

    FIELDS = ["employee_id", "name", "basic_salary", "allowance", "deduction"]

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
                employees = []
                for row in reader:
                    employees.append(Employee(
                        row["employee_id"], row["name"], row["basic_salary"],
                        row["allowance"], row["deduction"]
                    ))
                return employees
        except (OSError, csv.Error, KeyError) as error:
            raise ValueError(f"Could not read employee data: {error}")

    def save(self, employees):
        try:
            with self.file_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDS)
                writer.writeheader()
                for employee in employees:
                    writer.writerow(employee.to_row())
        except OSError as error:
            raise ValueError(f"Could not save employee data: {error}")


class PayrollManager:
    """Manages employee records and payroll operations."""

    def __init__(self, storage):
        self.storage = storage
        self.employees = self.storage.load()
        self._check_duplicate_ids(self.employees)

    @staticmethod
    def _check_duplicate_ids(employees):
        ids = [employee.employee_id.casefold() for employee in employees]
        if len(ids) != len(set(ids)):
            raise ValueError("Employee data contains duplicate IDs.")

    def add_employee(self, employee):
        if any(item.employee_id.casefold() == employee.employee_id.casefold()
               for item in self.employees):
            raise ValueError("An employee with this ID already exists.")
        self.employees.append(employee)
        self.storage.save(self.employees)

    def find_employee(self, employee_id):
        for employee in self.employees:
            if employee.employee_id.casefold() == employee_id.strip().casefold():
                return employee
        return None

    def update_employee(self, employee_id, replacement):
        old_employee = self.find_employee(employee_id)
        if old_employee is None:
            raise ValueError("Employee not found.")
        if replacement.employee_id.casefold() != old_employee.employee_id.casefold():
            if self.find_employee(replacement.employee_id):
                raise ValueError("An employee with this ID already exists.")
        index = self.employees.index(old_employee)
        self.employees[index] = replacement
        self.storage.save(self.employees)

    def delete_employee(self, employee_id):
        employee = self.find_employee(employee_id)
        if employee is None:
            raise ValueError("Employee not found.")
        self.employees.remove(employee)
        self.storage.save(self.employees)

    def display_employees(self):
        return list(self.employees)


def read_non_empty(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("This field cannot be empty.")
    return value


def read_employee():
    employee_id = read_non_empty("Employee ID: ")
    name = read_non_empty("Employee name: ")
    basic_salary = input("Basic monthly salary: ").strip()
    allowance = input("Allowance: ").strip()
    deduction = input("Deduction: ").strip()
    return Employee(employee_id, name, basic_salary, allowance, deduction)


def print_employee(employee):
    print(f"ID: {employee.employee_id} | Name: {employee.name}")
    print(f"Basic salary: {employee.basic_salary:.2f}")
    print(f"Allowance: {employee.allowance:.2f}")
    print(f"Gross salary: {employee.gross_salary:.2f}")
    print(f"Deduction: {employee.deduction:.2f}")
    print(f"Net salary: {employee.calculate_pay():.2f}")


def generate_payslip(employee):
    print("\n========== MONTHLY PAYSLIP ==========")
    print(f"Employee ID : {employee.employee_id}")
    print(f"Employee    : {employee.name}")
    print("-------------------------------------")
    print(f"Basic salary: {employee.basic_salary:.2f}")
    print(f"Allowance   : {employee.allowance:.2f}")
    print(f"Gross salary: {employee.gross_salary:.2f}")
    print(f"Deduction   : {employee.deduction:.2f}")
    print("-------------------------------------")
    print(f"NET PAY     : {employee.calculate_pay():.2f}")
    print("=====================================")


def show_menu():
    print("\n===== EMPLOYEE PAYROLL SYSTEM =====")
    print("1. Add employee")
    print("2. Display all employees")
    print("3. Search employee")
    print("4. Calculate salary / Generate payslip")
    print("5. Update employee")
    print("6. Delete employee")
    print("7. Exit")


def main():
    try:
        manager = PayrollManager(CSVStorage(DATA_FILE))
    except (ValueError, OSError) as error:
        print(f"Could not load employee data: {error}")
        return

    while True:
        show_menu()
        choice = input("Choose an option (1-7): ").strip()
        try:
            if choice == "1":
                employee = read_employee()
                manager.add_employee(employee)
                print("Employee added successfully.")
            elif choice == "2":
                employees = manager.display_employees()
                if not employees:
                    print("No employees found.")
                else:
                    for employee in employees:
                        print_employee(employee)
                        print("-" * 37)
            elif choice == "3":
                employee_id = read_non_empty("Enter employee ID to search: ")
                employee = manager.find_employee(employee_id)
                if employee:
                    print_employee(employee)
                else:
                    print("Employee not found.")
            elif choice == "4":
                employee_id = read_non_empty("Enter employee ID for payslip: ")
                employee = manager.find_employee(employee_id)
                if employee:
                    generate_payslip(employee)
                else:
                    print("Employee not found.")
            elif choice == "5":
                employee_id = read_non_empty("Enter employee ID to update: ")
                if manager.find_employee(employee_id) is None:
                    print("Employee not found.")
                else:
                    print("Enter the employee's new details.")
                    replacement = read_employee()
                    manager.update_employee(employee_id, replacement)
                    print("Employee updated successfully.")
            elif choice == "6":
                employee_id = read_non_empty("Enter employee ID to delete: ")
                manager.delete_employee(employee_id)
                print("Employee deleted successfully.")
            elif choice == "7":
                print("Goodbye.")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 7.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled. Exiting.")
            break


if __name__ == "__main__":
    main()
