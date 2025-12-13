# Week 3 Activity 5 – Clinic System

This folder contains the deliverables for the clinic scenario in Activity 5: an ER-style design (Patients, Doctors, Appointments) plus an OOP Python demo that runs on SQLite.

![Clinic ER Diagram](Activity%205.png)

[📹 2-minute walkthrough video](https://drive.google.com/file/d/1W_JtBApDdUZb-TbnC9fvXpl4nR3xnfhG/view?usp=sharing)

## Requirements covered
- Lists every patient classified as a senior (age > 65) with their full information.
- Shows the total number of ophthalmology specialists working in the clinic.
- Keeps each entity in its own class/module to mirror the ER diagram.

## Files
- `activity5.py` – entry script that creates tables, seeds demo data, and prints the reports.
- `clinic_db.py` – database helper that hides all raw SQL commands.
- `patient.py`, `doctor.py` – entity classes with simple `register()` helpers.
- `README.md` – this explanation and the embedded ER diagram (`Activity 5.png`).

## How to run
```bash
cd Week3/activity5
python3 activity5.py
```
Expected console output:
```
Senior patients (age > 65):
- #2 Marco Diaz, age 69, phone 555-2222
- #4 Omar Lee, age 77, phone 555-4444
- #1 Evelyn Smith, age 72, phone 555-1111

Number of ophthalmology specialists: 2
```
