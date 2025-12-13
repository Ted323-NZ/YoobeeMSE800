"""Database helper for Activity 5."""

import sqlite3
from pathlib import Path
from typing import List, Tuple

from doctor import Doctor
from patient import Patient


class ClinicDB:
    """Wraps all SQLite access for the clinic system."""

    def __init__(self, db_name: str = "clinic.db") -> None:
        self.path = Path(db_name)
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.close()

    def create_tables(self) -> None:
        """Build the patient and doctor tables plus helper relations."""
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Patients (
                    patient_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    phone TEXT NOT NULL
                );"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Doctors (
                    doctor_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    specialty TEXT NOT NULL
                );"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Appointments (
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doctor_id INTEGER NOT NULL,
                    patient_id INTEGER NOT NULL,
                    appointment_date TEXT NOT NULL,
                    diagnosis TEXT,
                    FOREIGN KEY(doctor_id) REFERENCES Doctors(doctor_id),
                    FOREIGN KEY(patient_id) REFERENCES Patients(patient_id)
                );"""
        )
        self.conn.commit()

    def reset_data(self) -> None:
        """Start with empty tables to keep demo output consistent."""
        for table in ("Appointments", "Patients", "Doctors"):
            self.cursor.execute(f"DELETE FROM {table};")
        self.conn.commit()

    def add_patient(self, patient: Patient) -> None:
        self.cursor.execute(
            "INSERT INTO Patients VALUES (?, ?, ?, ?, ?);",
            (patient.patient_id, patient.first_name, patient.last_name, patient.age, patient.phone),
        )

    def add_doctor(self, doctor: Doctor) -> None:
        self.cursor.execute(
            "INSERT INTO Doctors VALUES (?, ?, ?, ?);",
            (doctor.doctor_id, doctor.first_name, doctor.last_name, doctor.specialty),
        )

    def add_appointment(self, patient: Patient, doctor: Doctor, date: str, diagnosis: str) -> None:
        """Record an appointment between the given patient and doctor."""
        self.cursor.execute(
            "INSERT INTO Appointments (doctor_id, patient_id, appointment_date, diagnosis) VALUES (?, ?, ?, ?);",
            (doctor.doctor_id, patient.patient_id, date, diagnosis),
        )

    def list_senior_patients(self) -> List[Tuple]:
        """Return all patients older than 65."""
        self.cursor.execute(
            """SELECT patient_id, first_name, last_name, age, phone
                FROM Patients
                WHERE age > 65
                ORDER BY last_name;"""
        )
        return self.cursor.fetchall()

    def count_ophthalmology_doctors(self) -> int:
        """Count doctors with specialty Ophthalmology (case insensitive)."""
        self.cursor.execute(
            """SELECT COUNT(*)
                FROM Doctors
                WHERE LOWER(specialty) = 'ophthalmology';"""
        )
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def close(self) -> None:
        """Flush and close the database connection."""
        self.conn.commit()
        self.conn.close()
