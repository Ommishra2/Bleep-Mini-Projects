import csv
from abc import ABC, abstractmethod
from pathlib import Path

DATA_FILE = Path(__file__).with_name("patients.csv")


class PersonBase(ABC):
    """Abstract base class for people in the hospital system."""

    def __init__(self, person_id, name, age):
        self.person_id = person_id.strip()
        self.name = name.strip()
        try:
            self.age = int(age)
        except (TypeError, ValueError):
            raise ValueError("Age must be a whole number.")

    @abstractmethod
    def get_details(self):
        pass


class Patient(PersonBase):
    """Stores basic patient information."""

    def __init__(self, patient_id, name, age, condition, doctor):
        super().__init__(patient_id, name, age)
        self.condition = condition.strip()
        self.doctor = doctor.strip()
        self._validate()

    def _validate(self):
        if not self.person_id:
            raise ValueError("Patient ID cannot be empty.")
        if not self.name:
            raise ValueError("Patient name cannot be empty.")
        if self.age < 0 or self.age > 120:
            raise ValueError("Age must be between 0 and 120.")
        if not self.condition:
            raise ValueError("Condition cannot be empty.")
        if not self.doctor:
            raise ValueError("Doctor name cannot be empty.")

    @property
    def patient_id(self):
        return self.person_id

    def get_details(self):
        return (
            f"Patient ID: {self.patient_id}\n"
            f"Name: {self.name}\n"
            f"Age: {self.age}\n"
            f"Condition: {self.condition}\n"
            f"Doctor: {self.doctor}"
        )

    def to_row(self):
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": str(self.age),
            "condition": self.condition,
            "doctor": self.doctor,
        }


class CSVStorage:
    """Loads and saves patient data in a CSV file."""

    FIELDS = ["patient_id", "name", "age", "condition", "doctor"]

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
                return [
                    Patient(row["patient_id"], row["name"], row["age"],
                            row["condition"], row["doctor"])
                    for row in reader
                ]
        except (OSError, csv.Error, KeyError) as error:
            raise ValueError(f"Could not read patient data: {error}")

    def save(self, patients):
        try:
            with self.file_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDS)
                writer.writeheader()
                for patient in patients:
                    writer.writerow(patient.to_row())
        except OSError as error:
            raise ValueError(f"Could not save patient data: {error}")


class HospitalManager:
    """Manages patient records."""

    def __init__(self, storage):
        self.storage = storage
        self.patients = self.storage.load()
        ids = [patient.patient_id.casefold() for patient in self.patients]
        if len(ids) != len(set(ids)):
            raise ValueError("Patient data contains duplicate IDs.")

    def add_patient(self, patient):
        if self.find_patient(patient.patient_id):
            raise ValueError("A patient with this ID already exists.")
        self.patients.append(patient)
        self.storage.save(self.patients)

    def find_patient(self, patient_id):
        for patient in self.patients:
            if patient.patient_id.casefold() == patient_id.strip().casefold():
                return patient
        return None

    def list_patients(self):
        return list(self.patients)

    def update_patient(self, patient_id, replacement):
        old_patient = self.find_patient(patient_id)
        if old_patient is None:
            raise ValueError("Patient not found.")
        if replacement.patient_id.casefold() != old_patient.patient_id.casefold():
            if self.find_patient(replacement.patient_id):
                raise ValueError("A patient with this ID already exists.")
        self.patients[self.patients.index(old_patient)] = replacement
        self.storage.save(self.patients)

    def delete_patient(self, patient_id):
        patient = self.find_patient(patient_id)
        if patient is None:
            raise ValueError("Patient not found.")
        self.patients.remove(patient)
        self.storage.save(self.patients)


def read_non_empty(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("This field cannot be empty.")
    return value


def read_patient():
    patient_id = read_non_empty("Patient ID: ")
    name = read_non_empty("Patient name: ")
    age = input("Age: ").strip()
    condition = read_non_empty("Condition / reason for visit: ")
    doctor = read_non_empty("Assigned doctor: ")
    return Patient(patient_id, name, age, condition, doctor)


def show_menu():
    print("\n===== HOSPITAL MANAGEMENT SYSTEM =====")
    print("1. Register patient")
    print("2. Display all patients")
    print("3. Search patient")
    print("4. Update patient")
    print("5. Delete patient")
    print("6. Exit")


def main():
    try:
        manager = HospitalManager(CSVStorage(DATA_FILE))
    except (ValueError, OSError) as error:
        print(f"Could not load patient data: {error}")
        return

    while True:
        show_menu()
        choice = input("Choose an option (1-6): ").strip()
        try:
            if choice == "1":
                manager.add_patient(read_patient())
                print("Patient registered successfully.")
            elif choice == "2":
                patients = manager.list_patients()
                if not patients:
                    print("No patients found.")
                else:
                    for patient in patients:
                        print("-" * 35)
                        print(patient.get_details())
            elif choice == "3":
                patient_id = read_non_empty("Enter patient ID to search: ")
                patient = manager.find_patient(patient_id)
                if patient:
                    print(patient.get_details())
                else:
                    print("Patient not found.")
            elif choice == "4":
                patient_id = read_non_empty("Enter patient ID to update: ")
                if manager.find_patient(patient_id) is None:
                    print("Patient not found.")
                else:
                    print("Enter the patient's updated details.")
                    manager.update_patient(patient_id, read_patient())
                    print("Patient updated successfully.")
            elif choice == "5":
                patient_id = read_non_empty("Enter patient ID to delete: ")
                manager.delete_patient(patient_id)
                print("Patient deleted successfully.")
            elif choice == "6":
                print("Goodbye.")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 6.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled. Exiting.")
            break


if __name__ == "__main__":
    main()
