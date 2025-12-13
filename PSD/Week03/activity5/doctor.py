"""Doctor entity for Week 3 Activity 5."""

from dataclasses import dataclass


@dataclass
class Doctor:
    """Stores doctor details and can save itself."""

    doctor_id: int
    first_name: str
    last_name: str
    specialty: str

    def register(self, db: "ClinicDB") -> None:
        """Tell the DB helper to store this doctor."""
        db.add_doctor(self)
