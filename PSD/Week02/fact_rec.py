def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)


def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Factorial")
    print("2. Fibonacci")

    choice = input("Enter choice (1/2): ")

    if choice in ["1", "2"]:
        n = int(input("Enter a positive integer: "))

    if choice == "1":
        ans = factorial(n)
    elif choice == "2":
        ans = fibonacci(n)
    else:
        ans = "Invalid choice"

    print("\nFinal result:", ans)
