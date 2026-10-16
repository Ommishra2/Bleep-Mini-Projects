# Hospital Management System

A beginner-friendly Python OOP console application for managing basic patient records.

## Features
- Register patients
- Display all patient records
- Search patients by ID
- Update and delete patient records
- Store data in `patients.csv`
- Validate required fields and age
- Handle duplicate IDs, missing records, and file errors

## OOP concepts
- **Encapsulation:** patient information is grouped in a `Patient` object with validation.
- **Inheritance:** `Patient` inherits from `PersonBase`.
- **Abstraction:** `PersonBase` uses `ABC` and `@abstractmethod`.
- **Composition:** `HospitalManager` uses `CSVStorage`.

## Requirements
Python 3.9 or newer. No external packages are needed.

## Run
Open a terminal in this folder and run `python main.py`.

This is an educational demo and is not designed to store real patient or medical records.
