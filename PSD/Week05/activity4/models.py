"""
models.py

Inheritance Structure:
Person -> Student, Staff
Staff  -> General, Academic
"""

from typing import List


class Person:
    """
    Base class (Parent): Person

    This class stores common fields that all people share.
    """

    def __init__(self, person_id: int, name: str) -> None:
        self.person_id = person_id
        self.name = name

    def get_role(self) -> str:
        """
        This method is intended to be overridden by subclasses.
        """
        return "Person"

    def display_info(self) -> str:
        """
        Common method for displaying basic info.
        Subclasses can override this to add extra fields.
        """
        return f"{self.get_role()} | id={self.person_id}, name={self.name}"


class Student(Person):
    """
    Child class: Student inherits from Person
    UML fields (extra): student_id
    NOTE: name is inherited from Person (no need to redefine).
    """

    def __init__(self, person_id: int, name: str, student_id: str) -> None:
        # super() calls the parent constructor to initialize id and name
        super().__init__(person_id, name)
        self.student_id = student_id

    def get_role(self) -> str:
        # Override: a Student is not a generic Person
        return "Student"

    def display_info(self) -> str:
        # Extend parent method output with student-specific field
        base = super().display_info()
        return f"{base}, student_id={self.student_id}"


class Staff(Person):
    """
    Child class: Staff inherits from Person
    UML fields (extra): staff_id, tax_num
    """

    def __init__(self, person_id: int, name: str, staff_id: str, tax_num: str) -> None:
        super().__init__(person_id, name)
        self.staff_id = staff_id
        self.tax_num = tax_num

    def get_role(self) -> str:
        return "Staff"

    def display_info(self) -> str:
        base = super().display_info()
        return f"{base}, staff_id={self.staff_id}, tax_num={self.tax_num}"


class General(Staff):
    """
    Grandchild class: General inherits from Staff (and indirectly Person)
    (The UML box shows Id + rate_of_pay; in code we use the same person_id from Person.)
    """

    def __init__(
        self,
        person_id: int,
        name: str,
        staff_id: str,
        tax_num: str,
        rate_of_pay: float
    ) -> None:
        super().__init__(person_id, name, staff_id, tax_num)
        self.rate_of_pay = rate_of_pay

    def get_role(self) -> str:
        return "General"

    def calculate_pay(self, hours: float) -> float:
        """
        Example behavior for General staff:
        pay = rate_of_pay * hours
        """
        return self.rate_of_pay * hours

    def display_info(self) -> str:
        base = super().display_info()
        return f"{base}, rate_of_pay={self.rate_of_pay}"


class Academic(Staff):
    """
    Grandchild class: Academic inherits from Staff
    UML fields (extra): publications
    """

    def __init__(
        self,
        person_id: int,
        name: str,
        staff_id: str,
        tax_num: str,
        publications: List[str] | None = None
    ) -> None:
        super().__init__(person_id, name, staff_id, tax_num)
        # Store publications as a list; default to empty list if None
        self.publications = publications if publications is not None else []

    def get_role(self) -> str:
        return "Academic"

    def add_publication(self, title: str) -> None:
        """Add one publication title."""
        self.publications.append(title)

    def display_info(self) -> str:
        base = super().display_info()
        return f"{base}, publications_count={len(self.publications)}"
