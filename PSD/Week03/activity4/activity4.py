"""Week 3 Activity 4 – simple entry script tying all OOP pieces together."""

from college_db import CollegeDB
from course import Course
from student import Student
from teacher import Teacher


def seed_entities(db: CollegeDB) -> None:
    """Create the objects and ask each one to save itself."""
    students = [
        Student(1, "Alice"),
        Student(2, "Bob"),
        Student(3, "Cindy"),
        Student(4, "David"),
    ]
    teachers = [
        Teacher(1, "John Smith"),
        Teacher(2, "Amy Wilson"),
        Teacher(3, "Dr. Clark"),
    ]
    mse800 = Course("MSE800", "Research Methods")
    mse801 = Course("MSE801", "Quantum Computing")

    for student in students:
        student.register(db)
    for teacher in teachers:
        teacher.register(db)

    mse800.register(db)
    mse801.register(db)

    # Link students and teachers using the CollegeDB helper methods
    for student in students:
        db.enrol_student(student, mse800)  # Everyone studies MSE800

    for teacher in teachers[:2]:
        db.assign_teacher(teacher, mse801)  # First two teachers teach MSE801


def main() -> None:
    """Create tables, add sample data, and print the two answers we need."""
    with CollegeDB() as db:
        print(">>> Creating tables...")
        db.create_tables()
        db.reset_data()

        print(">>> Seeding deterministic demo data via Student/Teacher/Course objects...")
        seed_entities(db)

        # Show number of students for MSE800 (requirement 1)
        mse800_count = db.get_student_count_for_course("MSE800")
        print(f"\nNumber of students in MSE800: {mse800_count}")

        # Show list of teachers assigned to MSE801 (requirement 2)
        mse801_teachers = db.get_teachers_for_course("MSE801")
        print("\nTeachers teaching MSE801:")
        for teacher in mse801_teachers:
            print(f"- {teacher}")


if __name__ == "__main__":
    main()
