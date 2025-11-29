class MathSeries:
    """
    A class to calculate factorial and Fibonacci series using object-based implementation.
    """

    def __init__(self, n):
        self.n = n  # Store the user-provided number n for calculations

    # Recursive method to calculate factorial
    def factorial_recursive(self):
        if self.n < 0:
            raise ValueError("Factorial is not defined for negative numbers.")  # Raise error if n < 0
        if self.n in (0, 1):
            return 1  # Base case: 0! and 1! are 1
        # Recursive call: n! = n * (n-1)!
        return self.n * MathSeries(self.n - 1).factorial_recursive()

    # Recursive method to calculate a single Fibonacci number
    def fibonacci_recursive(self, index):
        if index < 0:
            raise ValueError("Fibonacci is not defined for negative numbers.")  # Error for negative index
        if index == 0:
            return 0  # Base case: F(0) = 0
        if index == 1:
            return 1  # Base case: F(1) = 1
        # Recursive call: F(n) = F(n-1) + F(n-2)
        return (MathSeries(index - 1).fibonacci_recursive(index - 1) +
                MathSeries(index - 2).fibonacci_recursive(index - 2))

    # Method to generate the full Fibonacci series as a list
    def fibonacci_series(self):
        series = []  # Initialize an empty list to store the series
        for i in range(self.n):
            series.append(self.fibonacci_recursive(i))  # Append each Fibonacci number
        return series  # Return the complete series


if __name__ == "__main__":
    # Ask the user for the number
    n = int(input("Enter the number for factorial and Fibonacci series: "))
    
    obj = MathSeries(n)  # Create an object with the user-provided number

    # Print factorial using recursive method
    print(f"Factorial of {n} (recursive):", obj.factorial_recursive())

    # Print the entire Fibonacci series of length n
    print(f"Fibonacci series of length {n} (recursive):", obj.fibonacci_series())
