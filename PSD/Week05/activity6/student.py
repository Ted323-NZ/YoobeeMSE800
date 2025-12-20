from person import Person, PersonPrivate


class Student(Person):
    def __init__(self, name, address, age, student_id):
        super().__init__(name, address, age)
        self.student_id = student_id

    def greet(self):
        print("Hi " + self._name)


class StudentPrivate(PersonPrivate):
    def __init__(self, name, address, age, student_id):
        super().__init__(name, address, age)
        self.student_id = student_id

    def greet(self):
        # This will fail because __name is private to PersonPrivate.
        try:
            print("Hi " + self.__name)
        except AttributeError as exc:
            print("Hi <error>", exc)


if __name__ == "__main__":
    print("Protected attribute (_name):")
    student1 = Student("Alice", "123 Main St", 20, "S12345")
    student1.greet()
    Person.greet(student1)
    print()

    print("Private attribute (__name):")
    student2 = StudentPrivate("Bob", "456 Queen St", 21, "S67890")
    student2.greet()
    PersonPrivate.greet(student2)
    print("Correct access via getter:", student2.get_name())
