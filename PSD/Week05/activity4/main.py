from models import Person, Student, Staff, General, Academic

def main() -> None:
    p = Person(1, "Alex Person")
    s = Student(2, "Sally Student", "STU-1001")
    st = Staff(3, "Sam Staff", "STA-2001", "TAX-888")
    g = General(4, "Gina General", "STA-3001", "TAX-777", 30.0)
    a = Academic(5, "Andy Academic", "STA-4001", "TAX-666")
    a.add_publication("Inheritance in OOP")
    a.add_publication("UML Basics")

    people: list[Person] = [p, s, st, g, a]

    print("=== Inheritance + Polymorphism Demo ===")
    for person in people:
        # Same method name, different output -> polymorphism
        print(person.display_info())

    print("\n=== Extra subclass behaviors ===")
    print(f"{g.name} weekly pay (40 hours): {g.calculate_pay(40):.2f}")
    print(f"{a.name} publications: {a.publications}")

if __name__ == "__main__":
    main()
