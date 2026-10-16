# Vehicle Rental Management System

A beginner-friendly Python OOP console application for maintaining a small vehicle fleet and tracking rentals.

## Features
- Add, display, and search vehicles
- List available vehicles
- Rent a vehicle for a specified number of days
- Calculate rental cost (daily rate × rental days)
- Return rented vehicles
- Delete available vehicles
- Save and load records in `rentals.csv`
- Validate inputs and handle duplicate IDs, unavailable vehicles, and file errors

## OOP concepts
- **Encapsulation:** daily rate and availability use private attributes.
- **Inheritance:** `Vehicle` inherits from `VehicleBase`.
- **Abstraction:** `VehicleBase` uses `ABC` and `@abstractmethod`.
- **Composition:** `RentalManager` uses `CSVStorage`.

## Requirements
Python 3.9 or newer. No external packages are required.

## Run
Open a terminal in this folder and run `python main.py`.
