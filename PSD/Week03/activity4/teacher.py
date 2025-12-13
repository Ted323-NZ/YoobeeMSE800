"""Teacher entity for Week 3 Activity 4."""

from dataclasses import dataclass


@dataclass
class Teacher:
    """Simple data bag for the teacher id and name."""

    teacher_id: int
    name: str

    def register(self, db: "CollegeDB") -> None:
        """Tell the database helper to store this teacher."""
        db.add_teacher(self)
