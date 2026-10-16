# Bank Account Management System

A simple educational Python console project. It is not real banking software.

## Run
`python main.py`

## Features
- Create and display accounts
- Search account and check balance
- Deposit and withdraw
- Reject negative/zero transactions and overdrafts
- Delete accounts
- Save/load accounts using CSV
- Validate IDs and handle file/input errors

## OOP requirements
- Classes and objects: `AccountBase`, `BankAccount`, `CSVStorage`, `BankManager`
- Encapsulation: private attributes with validated properties
- Inheritance: `BankAccount` inherits from `AccountBase`
- Abstraction: `AccountBase` uses `abc.ABC` and `@abstractmethod`
- File handling: CSV reader/writer
- Exception handling: invalid values, missing accounts, duplicate IDs, file errors

## Tests
Run `python -m unittest -v`. Tests use temporary files and do not alter the sample data.
