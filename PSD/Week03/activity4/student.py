"""Student entity for Week 3 Activity 4."""

from dataclasses import dataclass


@dataclass
class Student:
    """Holds the student id and name and knows how to save itself."""

    student_id: int
    name: str

    def register(self, db: "CollegeDB") -> None:
        """Tell the database helper to store this student."""
        db.add_student(self)
