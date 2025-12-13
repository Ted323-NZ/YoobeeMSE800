"""Database helper class for Activity 4."""

import sqlite3
from pathlib import Path
from typing import List

from course import Course
from student import Student
from teacher import Teacher


class CollegeDB:
    """Wraps every direct call to SQLite."""

    def __init__(self, db_name: str = "college.db") -> None:
        # Connect to the SQLite database file (created automatically if missing)
        self.db_path = Path(db_name)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON;")  # Enforce referential integrity

    def __enter__(self):
        # Allow usage with `with CollegeDB() as db:`
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        # Close the connection automatically when leaving the context manager
        self.close()

    def create_tables(self) -> None:
        """Build all tables we need if they are missing."""
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Students (
                    student_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Teachers (
                    teacher_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Courses (
                    course_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL
                );"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Enrolments (
                    student_id INTEGER NOT NULL,
                    course_id TEXT NOT NULL,
                    FOREIGN KEY(student_id) REFERENCES Students(student_id),
                    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
                );"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Teaching (
                    teacher_id INTEGER NOT NULL,
                    course_id TEXT NOT NULL,
                    FOREIGN KEY(teacher_id) REFERENCES Teachers(teacher_id),
                    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
                );"""
        )
        self.conn.commit()

    def reset_data(self) -> None:
        """Clear the tables so each run starts fresh."""
        for table in ("Enrolments", "Teaching", "Students", "Teachers", "Courses"):
            self.cursor.execute(f"DELETE FROM {table};")
        self.conn.commit()

    # === CRUD helpers for each entity type ===
    def add_student(self, student: Student) -> None:
        self.cursor.execute("INSERT INTO Students VALUES (?, ?);", (student.student_id, student.name))

    def add_teacher(self, teacher: Teacher) -> None:
        self.cursor.execute("INSERT INTO Teachers VALUES (?, ?);", (teacher.teacher_id, teacher.name))

    def add_course(self, course: Course) -> None:
        self.cursor.execute("INSERT INTO Courses VALUES (?, ?);", (course.course_id, course.title))

    def enrol_student(self, student: Student, course: Course) -> None:
        """Link a student to a course."""
        self.cursor.execute("INSERT INTO Enrolments VALUES (?, ?);", (student.student_id, course.course_id))

    def assign_teacher(self, teacher: Teacher, course: Course) -> None:
        """Link a teacher to a course."""
        self.cursor.execute("INSERT INTO Teaching VALUES (?, ?);", (teacher.teacher_id, course.course_id))

    # === Reporting helpers ===
    def get_student_count_for_course(self, course_code: str) -> int:
        """Count how many students picked the given course."""
        self.cursor.execute(
            """SELECT COUNT(DISTINCT student_id)
                FROM Enrolments
                WHERE course_id = ?;""",
            (course_code,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_teachers_for_course(self, course_code: str) -> List[str]:
        """List every teacher linked to the given course."""
        self.cursor.execute(
            """SELECT Teachers.name
                FROM Teaching
                JOIN Teachers ON Teachers.teacher_id = Teaching.teacher_id
                WHERE Teaching.course_id = ?
                ORDER BY Teachers.name;""",
            (course_code,),
        )
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def close(self) -> None:
        """Save changes and close the connection."""
        self.conn.commit()
        self.conn.close()
