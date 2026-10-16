import csv
from abc import ABC, abstractmethod
from pathlib import Path

DATA_FILE = Path(__file__).with_name("rentals.csv")


class VehicleBase(ABC):
    """Abstract base class for vehicles."""

    def __init__(self, vehicle_id, model):
        self.vehicle_id = vehicle_id.strip()
        self.model = model.strip()

    @abstractmethod
    def rental_cost(self, days):
        pass


class Vehicle(VehicleBase):
    """Represents a vehicle that can be rented."""

    def __init__(self, vehicle_id, model, category, daily_rate, available=True):
        super().__init__(vehicle_id, model)
        self.category = category.strip().title()
        try:
            self.__daily_rate = float(daily_rate)
        except (TypeError, ValueError):
            raise ValueError("Daily rate must be a valid number.")
        self.__available = self._parse_available(available)
        self._validate()

    @staticmethod
    def _parse_available(value):
        if isinstance(value, bool):
            return value
        text = str(value).strip().lower()
        if text in ("true", "yes", "1"):
            return True
        if text in ("false", "no", "0"):
            return False
        raise ValueError("Availability must be true or false.")

    def _validate(self):
        if not self.vehicle_id:
            raise ValueError("Vehicle ID cannot be empty.")
        if not self.model:
            raise ValueError("Vehicle model cannot be empty.")
        if not self.category:
            raise ValueError("Vehicle category cannot be empty.")
        if self.__daily_rate < 0:
            raise ValueError("Daily rate cannot be negative.")

    @property
    def daily_rate(self):
        return self.__daily_rate

    @property
    def available(self):
        return self.__available

    def rental_cost(self, days):
        try:
            days = int(days)
        except (TypeError, ValueError):
            raise ValueError("Rental days must be a whole number.")
        if days <= 0:
            raise ValueError("Rental days must be greater than zero.")
        return round(self.__daily_rate * days, 2)

    def rent(self):
        if not self.__available:
            raise ValueError("This vehicle is already rented.")
        self.__available = False

    def return_vehicle(self):
        if self.__available:
            raise ValueError("This vehicle is already available.")
        self.__available = True

    def to_row(self):
        return {
            "vehicle_id": self.vehicle_id,
            "model": self.model,
            "category": self.category,
            "daily_rate": f"{self.daily_rate:.2f}",
            "available": str(self.available),
        }


class CSVStorage:
    FIELDS = ["vehicle_id", "model", "category", "daily_rate", "available"]

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
                    Vehicle(row["vehicle_id"], row["model"], row["category"],
                            row["daily_rate"], row["available"])
                    for row in reader
                ]
        except (OSError, csv.Error, KeyError) as error:
            raise ValueError(f"Could not read vehicle data: {error}")

    def save(self, vehicles):
        try:
            with self.file_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDS)
                writer.writeheader()
                for vehicle in vehicles:
                    writer.writerow(vehicle.to_row())
        except OSError as error:
            raise ValueError(f"Could not save vehicle data: {error}")


class RentalManager:
    def __init__(self, storage):
        self.storage = storage
        self.vehicles = self.storage.load()
        ids = [vehicle.vehicle_id.casefold() for vehicle in self.vehicles]
        if len(ids) != len(set(ids)):
            raise ValueError("Vehicle data contains duplicate IDs.")

    def add_vehicle(self, vehicle):
        if self.find_vehicle(vehicle.vehicle_id):
            raise ValueError("A vehicle with this ID already exists.")
        self.vehicles.append(vehicle)
        self.storage.save(self.vehicles)

    def find_vehicle(self, vehicle_id):
        for vehicle in self.vehicles:
            if vehicle.vehicle_id.casefold() == vehicle_id.strip().casefold():
                return vehicle
        return None

    def list_vehicles(self):
        return list(self.vehicles)

    def available_vehicles(self):
        return [vehicle for vehicle in self.vehicles if vehicle.available]

    def rent_vehicle(self, vehicle_id, days):
        vehicle = self.find_vehicle(vehicle_id)
        if vehicle is None:
            raise ValueError("Vehicle not found.")
        cost = vehicle.rental_cost(days)
        vehicle.rent()
        self.storage.save(self.vehicles)
        return cost

    def return_vehicle(self, vehicle_id):
        vehicle = self.find_vehicle(vehicle_id)
        if vehicle is None:
            raise ValueError("Vehicle not found.")
        vehicle.return_vehicle()
        self.storage.save(self.vehicles)

    def delete_vehicle(self, vehicle_id):
        vehicle = self.find_vehicle(vehicle_id)
        if vehicle is None:
            raise ValueError("Vehicle not found.")
        if not vehicle.available:
            raise ValueError("Return the vehicle before deleting it.")
        self.vehicles.remove(vehicle)
        self.storage.save(self.vehicles)


def read_non_empty(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("This field cannot be empty.")
    return value


def read_vehicle():
    vehicle_id = read_non_empty("Vehicle ID: ")
    model = read_non_empty("Vehicle model: ")
    category = read_non_empty("Category (Car/Bike/Van): ")
    daily_rate = input("Daily rental rate: ").strip()
    return Vehicle(vehicle_id, model, category, daily_rate)


def print_vehicle(vehicle):
    status = "Available" if vehicle.available else "Rented"
    print(f"ID: {vehicle.vehicle_id} | Model: {vehicle.model}")
    print(f"Category: {vehicle.category}")
    print(f"Daily rate: {vehicle.daily_rate:.2f}")
    print(f"Status: {status}")


def show_menu():
    print("\n===== VEHICLE RENTAL SYSTEM =====")
    print("1. Add vehicle")
    print("2. Display all vehicles")
    print("3. Display available vehicles")
    print("4. Search vehicle")
    print("5. Rent vehicle")
    print("6. Return vehicle")
    print("7. Delete vehicle")
    print("8. Exit")


def main():
    try:
        manager = RentalManager(CSVStorage(DATA_FILE))
    except (ValueError, OSError) as error:
        print(f"Could not load vehicle data: {error}")
        return

    while True:
        show_menu()
        choice = input("Choose an option (1-8): ").strip()
        try:
            if choice == "1":
                manager.add_vehicle(read_vehicle())
                print("Vehicle added successfully.")
            elif choice == "2":
                vehicles = manager.list_vehicles()
                if not vehicles:
                    print("No vehicles found.")
                else:
                    for vehicle in vehicles:
                        print_vehicle(vehicle)
                        print("-" * 30)
            elif choice == "3":
                vehicles = manager.available_vehicles()
                if not vehicles:
                    print("No vehicles are currently available.")
                else:
                    for vehicle in vehicles:
                        print_vehicle(vehicle)
            elif choice == "4":
                vehicle = manager.find_vehicle(read_non_empty("Enter vehicle ID: "))
                if vehicle:
                    print_vehicle(vehicle)
                else:
                    print("Vehicle not found.")
            elif choice == "5":
                vehicle_id = read_non_empty("Enter vehicle ID to rent: ")
                days = input("Number of rental days: ").strip()
                cost = manager.rent_vehicle(vehicle_id, days)
                print(f"Vehicle rented successfully. Rental cost: {cost:.2f}")
            elif choice == "6":
                manager.return_vehicle(read_non_empty("Enter vehicle ID to return: "))
                print("Vehicle returned successfully.")
            elif choice == "7":
                manager.delete_vehicle(read_non_empty("Enter vehicle ID to delete: "))
                print("Vehicle deleted successfully.")
            elif choice == "8":
                print("Goodbye.")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 8.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled. Exiting.")
            break


if __name__ == "__main__":
    main()
