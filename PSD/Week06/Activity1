class StudentRecords:
    def __init__(self):
        # Part 1: Two separate dictionaries
        self.student_names = {}   # {student_id: name}
        self.student_scores = {}  # {student_id: score}

    def add_student(self, student_id: str, name: str, score: float) -> None:
        """Add or update student info"""
        self.student_names[student_id] = name
        self.student_scores[student_id] = score

    def combine_records(self) -> dict:
        """
        Part 2: Combine the two dictionaries into a new one
        Format: {student_id: {"name": xxx, "score": xxx}}
        """
        combined = {}
        for student_id in self.student_names:
            # If some ID isn't in the scores dict, set score to None
            score = self.student_scores.get(student_id, None)
            combined[student_id] = {"name": self.student_names[student_id], "score": score}
        return combined

    def passed_students(self, pass_mark: float = 50.0) -> dict:
        """
        Part 2: Only keep students who passed (score >= 50)
        """
        combined = self.combine_records()
        passed = {}

        for student_id, info in combined.items():
            score = info["score"]
            if score is not None and score >= pass_mark:
                passed[student_id] = info

        return passed


def main():
    records = StudentRecords()

    # Part 1: 5 students 
    records.add_student("S001", "Alice", 78)
    records.add_student("S002", "Bob", 45)
    records.add_student("S003", "Charlie", 50)
    records.add_student("S004", "Diana", 92)
    records.add_student("S005", "Ethan", 39)

    # Part 2: Combine and filter out passed students
    combined = records.combine_records()
    passed = records.passed_students()

    print("=== Combined Dictionary ===")
    print(combined)

    print("\n=== Passed Students (>=50) ===")
    print(passed)


if __name__ == "__main__":
    main()
