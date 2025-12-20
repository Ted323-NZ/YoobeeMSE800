"""
main.py

Demonstrates inheritance and polymorphism:
- All objects are treated as Animal
- Calling describe() and move() behaves differently depending on the subclass
"""

from animals import Dog, Cat, Eagle, Penguin, Salmon, Shark, Animal


def main() -> None:
    # Create instances following the UML structure
    animals: list[Animal] = [
        Dog(name="Buddy", feature="fur"),
        Cat(name="Mimi", feature="fur"),
        Eagle(name="Sky", feature="feathers"),
        Penguin(name="Pingo", feature="feathers"),
        Salmon(name="Sally", feature="gills"),
        Shark(name="Bruce", feature="gills"),
    ]

    print("=== Inheritance + Polymorphism Demo ===")
    for a in animals:
        # Same method calls, different outputs -> polymorphism
        print(a.describe())
        a.move()


if __name__ == "__main__":
    main()
