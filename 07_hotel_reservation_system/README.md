# Hotel Reservation Management System

A beginner-friendly Python OOP console application for managing hotel reservations and calculating room costs.

## Features
- Add and display reservations
- Search reservations by ID
- Update and cancel reservations
- Calculate total cost from nights × nightly rate
- Save and load data in `reservations.csv`
- Validate input and handle missing records and file errors

## OOP concepts
- **Encapsulation:** nights and nightly rate are private attributes.
- **Inheritance:** `Reservation` inherits from `ReservationBase`.
- **Abstraction:** `ReservationBase` uses `ABC` and `@abstractmethod`.
- **Composition:** `HotelManager` uses `CSVStorage`.

## Requirements
Python 3.9 or newer. No external packages are required.

## Run
Open a terminal in this folder and run `python main.py`.
