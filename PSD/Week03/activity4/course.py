"""Course entity for Week 3 Activity 4."""

from dataclasses import dataclass


@dataclass
class Course:
    """Stores the course code, name, and can save itself."""

    course_id: str
    title: str

    def register(self, db: "CollegeDB") -> None:
        """Tell the database helper to store this course."""
        db.add_course(self)
