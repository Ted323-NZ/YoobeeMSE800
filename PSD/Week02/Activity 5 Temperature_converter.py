
class TemperatureConverter:

    def convert(self, temp_input):
        # basic input check
        if not temp_input or len(temp_input) < 2:
            return None

        # first char: F or C, rest: number
        prefix = temp_input[0]
        number_part = temp_input[1:]

        # check prefix and number
        if prefix not in ('F', 'C'):
            return None
        if not number_part.isdigit():
            return None

        value = float(number_part)

        # F -> C
        if prefix == 'F':
            c = (value - 32) * 5 / 9
            return f"{temp_input} degrees Fahrenheit is converted to {c:.2f} degrees Celsius"

        # C -> F
        elif prefix == 'C':
            f = value * 9 / 5 + 32
            return f"{temp_input} degrees Celsius is converted to {f:.2f} degrees Fahrenheit"


if __name__ == "__main__":
    converter = TemperatureConverter()

    user_input = input("Enter a temperature (e.g., F51 or C11): ")

    result = converter.convert(user_input)

    if result is None:
        print("Invalid input. Please enter the temperature with the correct 'C' or 'F' prefix.")
    else:
        print(result)
