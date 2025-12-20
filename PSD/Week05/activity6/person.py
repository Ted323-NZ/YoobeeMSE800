class Person:
    def __init__(self, name, address, age):
        # Protected attribute: intended for subclasses
        self._name = name
        self.address = address
        self.age = age

    def greet(self):
        print("Greetings and felicitations from the maestro " + self._name)


class PersonPrivate:
    def __init__(self, name, address, age):
        # Private attribute: name mangled to _PersonPrivate__name
        self.__name = name
        self.address = address
        self.age = age

    def greet(self):
        print("Greetings and felicitations from the maestro " + self.__name)

    def get_name(self):
        return self.__name
