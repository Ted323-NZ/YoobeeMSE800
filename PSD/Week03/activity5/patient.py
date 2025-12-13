"""Patient entity for Week 3 Activity 5."""

from dataclasses import dataclass


@dataclass
class Patient:
    """Stores patient demographics and can save itself."""

    patient_id: int
    first_name: str
    last_name: str
    age: int
    phone: str

    def register(self, db: "ClinicDB") -> None:
        """Tell the DB helper to store this patient."""
        db.add_patient(self)
