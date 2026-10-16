import csv
from abc import ABC, abstractmethod
from pathlib import Path

DATA_FILE = Path(__file__).with_name("reservations.csv")


class ReservationBase(ABC):
    """Abstract base class for reservations."""

    def __init__(self, reservation_id, guest_name):
        self.reservation_id = reservation_id.strip()
        self.guest_name = guest_name.strip()

    @abstractmethod
    def calculate_cost(self):
        pass


class Reservation(ReservationBase):
    """Stores a hotel reservation and calculates its total cost."""

    def __init__(self, reservation_id, guest_name, room_type, nights, nightly_rate):
        super().__init__(reservation_id, guest_name)
        self.room_type = room_type.strip().title()
        try:
            self.__nights = int(nights)
        except (TypeError, ValueError):
            raise ValueError("Number of nights must be a whole number.")
        try:
            self.__nightly_rate = float(nightly_rate)
        except (TypeError, ValueError):
            raise ValueError("Nightly rate must be a valid number.")
        self._validate()

    def _validate(self):
        if not self.reservation_id:
            raise ValueError("Reservation ID cannot be empty.")
        if not self.guest_name:
            raise ValueError("Guest name cannot be empty.")
        if not self.room_type:
            raise ValueError("Room type cannot be empty.")
        if self.__nights <= 0:
            raise ValueError("Number of nights must be greater than zero.")
        if self.__nightly_rate < 0:
            raise ValueError("Nightly rate cannot be negative.")

    @property
    def nights(self):
        return self.__nights

    @property
    def nightly_rate(self):
        return self.__nightly_rate

    def calculate_cost(self):
        return round(self.__nights * self.__nightly_rate, 2)

    def to_row(self):
        return {
            "reservation_id": self.reservation_id,
            "guest_name": self.guest_name,
            "room_type": self.room_type,
            "nights": str(self.nights),
            "nightly_rate": f"{self.nightly_rate:.2f}",
        }


class CSVStorage:
    """Reads and writes reservation records in a CSV file."""

    FIELDS = ["reservation_id", "guest_name", "room_type", "nights", "nightly_rate"]

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
                    Reservation(row["reservation_id"], row["guest_name"],
                                row["room_type"], row["nights"], row["nightly_rate"])
                    for row in reader
                ]
        except (OSError, csv.Error, KeyError) as error:
            raise ValueError(f"Could not read reservations: {error}")

    def save(self, reservations):
        try:
            with self.file_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDS)
                writer.writeheader()
                for reservation in reservations:
                    writer.writerow(reservation.to_row())
        except OSError as error:
            raise ValueError(f"Could not save reservations: {error}")


class HotelManager:
    """Manages hotel reservation records."""

    def __init__(self, storage):
        self.storage = storage
        self.reservations = self.storage.load()
        ids = [item.reservation_id.casefold() for item in self.reservations]
        if len(ids) != len(set(ids)):
            raise ValueError("Reservation data contains duplicate IDs.")

    def add_reservation(self, reservation):
        if self.find_reservation(reservation.reservation_id):
            raise ValueError("A reservation with this ID already exists.")
        self.reservations.append(reservation)
        self.storage.save(self.reservations)

    def find_reservation(self, reservation_id):
        for reservation in self.reservations:
            if reservation.reservation_id.casefold() == reservation_id.strip().casefold():
                return reservation
        return None

    def list_reservations(self):
        return list(self.reservations)

    def update_reservation(self, reservation_id, replacement):
        old = self.find_reservation(reservation_id)
        if old is None:
            raise ValueError("Reservation not found.")
        if replacement.reservation_id.casefold() != old.reservation_id.casefold():
            if self.find_reservation(replacement.reservation_id):
                raise ValueError("A reservation with this ID already exists.")
        self.reservations[self.reservations.index(old)] = replacement
        self.storage.save(self.reservations)

    def cancel_reservation(self, reservation_id):
        reservation = self.find_reservation(reservation_id)
        if reservation is None:
            raise ValueError("Reservation not found.")
        self.reservations.remove(reservation)
        self.storage.save(self.reservations)


def read_non_empty(prompt):
    value = input(prompt).strip()
    if not value:
        raise ValueError("This field cannot be empty.")
    return value


def read_reservation():
    reservation_id = read_non_empty("Reservation ID: ")
    guest_name = read_non_empty("Guest name: ")
    room_type = read_non_empty("Room type (Single/Double/Suite): ")
    nights = input("Number of nights: ").strip()
    nightly_rate = input("Rate per night: ").strip()
    return Reservation(reservation_id, guest_name, room_type, nights, nightly_rate)


def print_reservation(reservation):
    print(f"Reservation ID: {reservation.reservation_id}")
    print(f"Guest: {reservation.guest_name}")
    print(f"Room type: {reservation.room_type}")
    print(f"Nights: {reservation.nights}")
    print(f"Rate per night: {reservation.nightly_rate:.2f}")
    print(f"Total cost: {reservation.calculate_cost():.2f}")


def show_menu():
    print("\n===== HOTEL RESERVATION SYSTEM =====")
    print("1. Add reservation")
    print("2. Display all reservations")
    print("3. Search reservation")
    print("4. Update reservation")
    print("5. Cancel reservation")
    print("6. Exit")


def main():
    try:
        manager = HotelManager(CSVStorage(DATA_FILE))
    except (ValueError, OSError) as error:
        print(f"Could not load reservations: {error}")
        return
    while True:
        show_menu()
        choice = input("Choose an option (1-6): ").strip()
        try:
            if choice == "1":
                manager.add_reservation(read_reservation())
                print("Reservation created successfully.")
            elif choice == "2":
                reservations = manager.list_reservations()
                if not reservations:
                    print("No reservations found.")
                else:
                    for reservation in reservations:
                        print("-" * 35)
                        print_reservation(reservation)
            elif choice == "3":
                reservation = manager.find_reservation(
                    read_non_empty("Enter reservation ID to search: "))
                if reservation:
                    print_reservation(reservation)
                else:
                    print("Reservation not found.")
            elif choice == "4":
                reservation_id = read_non_empty("Enter reservation ID to update: ")
                if manager.find_reservation(reservation_id) is None:
                    print("Reservation not found.")
                else:
                    print("Enter the updated reservation details.")
                    manager.update_reservation(reservation_id, read_reservation())
                    print("Reservation updated successfully.")
            elif choice == "5":
                reservation_id = read_non_empty("Enter reservation ID to cancel: ")
                manager.cancel_reservation(reservation_id)
                print("Reservation cancelled successfully.")
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
