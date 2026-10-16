# Banking Transaction Management System

A beginner-friendly Python OOP console application for recording and reviewing deposit and withdrawal transactions.

## Features
- Record deposits and withdrawals
- Display all transactions
- Search by transaction ID
- Display transactions for a particular account ID
- Calculate recorded deposits, withdrawals, and net transaction total
- Save and load records in `transactions.csv`
- Validate transaction IDs, types, and positive amounts

## Important note
This educational program records transactions only. It does not connect to a bank, authenticate users, transfer money, or maintain an authoritative live bank balance. The account total is calculated from transactions stored in this CSV file.

## OOP concepts
- **Encapsulation:** transaction details are grouped in objects and validated.
- **Inheritance:** `BankTransaction` inherits from `TransactionBase`.
- **Abstraction:** `TransactionBase` uses `ABC` and `@abstractmethod`.
- **Composition:** `TransactionManager` uses `CSVStorage`.

## Requirements
Python 3.9 or newer. No external packages are required.

## Run
Open a terminal in this folder and run `python main.py`.
