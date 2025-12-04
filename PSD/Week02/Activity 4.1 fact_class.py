# Week 2 - Activity 4.1

class MathSeries:

    def factorial(self, n):
        if n <= 1:
            return 1
        return n * self.factorial(n - 1)

    def fibonacci(self, n):
        if n <= 1:
            return n
        return self.fibonacci(n - 1) + self.fibonacci(n - 2)


if __name__ == "__main__":
    calc = MathSeries()

    print("Choose an option:")
    print("1. Factorial")
    print("2. Fibonacci")

    choice = input("Enter choice (1/2): ")

    if choice in ("1", "2"):
        n = int(input("Enter a number: "))

    if choice == "1":
        print("Result:", calc.factorial(n))
    elif choice == "2":
        print("Result:", calc.fibonacci(n))
    else:
        print("Invalid choice")
