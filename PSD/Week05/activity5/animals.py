class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def describe(self) -> str:
        return f"Animal | name={self.name}"

    def move(self) -> None:
        print(f"{self.name} moves in a general way.")


class Mammal(Animal):
    def __init__(self, name: str, feature: str) -> None:
        super().__init__(name)
        self.feature = feature


class Bird(Animal):
    def __init__(self, name: str, feature: str) -> None:
        super().__init__(name)
        self.feature = feature


class Fish(Animal):
    def __init__(self, name: str, feature: str) -> None:
        super().__init__(name)
        self.feature = feature


class Dog(Mammal):
    def walk(self) -> None:
        print(f"{self.name} is walking (Dog).")

    def move(self) -> None:
        self.walk()


class Cat(Mammal):
    def walk(self) -> None:
        print(f"{self.name} is walking (Cat).")

    def move(self) -> None:
        self.walk()


class Eagle(Bird):
    def fly(self) -> None:
        print(f"{self.name} is flying (Eagle).")

    def move(self) -> None:
        self.fly()


class Penguin(Bird):
    def swim(self) -> None:
        print(f"{self.name} is swimming (Penguin).")

    def move(self) -> None:
        self.swim()


class Salmon(Fish):
    def swim(self) -> None:
        print(f"{self.name} is swimming (Salmon).")

    def move(self) -> None:
        self.swim()


class Shark(Fish):
    def swim(self) -> None:
        print(f"{self.name} is swimming (Shark).")

    def move(self) -> None:
        self.swim()
