import sqlite3
from typing import List, Tuple


class StudentDB:
    def __init__(self, db_name: str = "students.db"):
        self.db_name = db_name
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _create_table(self) -> None:
        """Create Student table with at least 3 attributes."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Student (
                    student_id   TEXT PRIMARY KEY,
                    student_name TEXT NOT NULL,
                    score        REAL NOT NULL
                )
            """)
            conn.commit()

    def upsert_student(self, student_id: str, student_name: str, score: float) -> None:
        """Insert or update a student record."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Student (student_id, student_name, score)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id) DO UPDATE SET
                    student_name = excluded.student_name,
                    score = excluded.score
            """, (student_id, student_name, score))
            conn.commit()

    def get_top_students(self, limit: int = 3) -> List[Tuple[str, str, float]]:
        """Return top N students by score (desc)."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT student_id, student_name, score
                FROM Student
                ORDER BY score DESC, student_id ASC
                LIMIT ?
            """, (limit,))
            return cur.fetchall()

    def get_passed_students(self, pass_mark: float = 50.0) -> List[Tuple[str, str, float]]:
        """Optional: retrieve only passed students from DB."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT student_id, student_name, score
                FROM Student
                WHERE score >= ?
                ORDER BY score DESC
            """, (pass_mark,))
            return cur.fetchall()


class StudentRecords:
    """
    W6-A1 + Database integration:
    - still keeps two dictionaries (names & scores)
    - stores data into SQLite Student table
    - can query Top 3 using SQL
    """
    def __init__(self, db: StudentDB):
        self.student_names = {}   # {student_id: name}
        self.student_scores = {}  # {student_id: score}
        self.db = db

    def add_student(self, student_id: str, name: str, score: float) -> None:
        self.student_names[student_id] = name
        self.student_scores[student_id] = score
        # integrate with database
        self.db.upsert_student(student_id, name, score)

    def combine_records(self) -> dict:
        combined = {}
        for sid in self.student_names:
            combined[sid] = {
                "name": self.student_names[sid],
                "score": self.student_scores.get(sid)
            }
        return combined

    def passed_students(self, pass_mark: float = 50.0) -> dict:
        combined = self.combine_records()
        return {sid: info for sid, info in combined.items()
                if info["score"] is not None and info["score"] >= pass_mark}


def main():
    db = StudentDB("students.db")
    records = StudentRecords(db)

        # Example 5 students 
    records.add_student("A102", "Mia Chen", 67)
    records.add_student("A117", "Noah Patel", 84)
    records.add_student("A131", "Sofia Nguyen", 49)
    records.add_student("A145", "Lucas Martins", 73)
    records.add_student("A158", "Zara Ibrahim", 58)


    # SQL Query: Top 3 students by score
    top3 = db.get_top_students(limit=3)

    print("=== Top 3 Students (SQL Query) ===")
    for sid, name, score in top3:
        print(f"{sid} | {name} | {score}")

    
    passed_dict = records.passed_students()
    print("\n=== Passed Students (Dictionary Filter, >=50) ===")
    print(passed_dict)


if __name__ == "__main__":
    main()
