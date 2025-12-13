"""Week 3 Activity 5 Clinic OOP demo."""

from clinic_db import ClinicDB
from doctor import Doctor
from patient import Patient


def seed_demo_data(db: ClinicDB) -> None:
    """Create sample patients, doctors, and a couple of appointments."""
    patients = [
        Patient(1, "Evelyn", "Smith", 72, "555-1111"),
        Patient(2, "Marco", "Diaz", 69, "555-2222"),
        Patient(3, "Lena", "Hart", 54, "555-3333"),
        Patient(4, "Omar", "Lee", 77, "555-4444"),
    ]
    doctors = [
        Doctor(1, "Priya", "Khan", "Ophthalmology"),
        Doctor(2, "James", "Chung", "Ophthalmology"),
        Doctor(3, "Sara", "Ng", "Dermatology"),
    ]

    for patient in patients:
        patient.register(db)
    for doctor in doctors:
        doctor.register(db)


    db.add_appointment(patients[0], doctors[0], "2024-12-01", "Routine eye exam")
    db.add_appointment(patients[1], doctors[1], "2024-12-02", "Follow-up for cataract")
    db.add_appointment(patients[2], doctors[2], "2024-12-03", "Skin rash consultation")


def main() -> None:
    """Create the schema, seed data, and print the required clinic stats."""
    with ClinicDB() as db:
        print(">>> Creating tables...")
        db.create_tables()
        db.reset_data()

        print(">>> Seeding demo patients/doctors...")
        seed_demo_data(db)

        print("\nSenior patients (age > 65):")
        seniors = db.list_senior_patients()
        for patient in seniors:
            patient_id, first_name, last_name, age, phone = patient
            print(f"- #{patient_id} {first_name} {last_name}, age {age}, phone {phone}")

        total_eye_docs = db.count_ophthalmology_doctors()
        print(f"\nNumber of ophthalmology specialists: {total_eye_docs}")


if __name__ == "__main__":
    main()
