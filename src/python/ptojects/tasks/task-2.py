class Calculator:
    def __init__(self, a, b):
        """Initializes the calculator class."""
        self.a = a
        self.b = b

    def add(self):
        """Add two numbers."""
        return self.a + self.b

    def subtract(self):
        """Subtract two numbers."""
        return self.a - self.b

    def multiply(self):
        """Multiply two numbers."""
        return self.a * self.b

    def divide(self):
        """Divide two numbers."""
        if self.b == 0:
            return "Cannot divide by zero"
        return self.a / self.b

    def calculator(self):
        """Main calculator logic to get user input and perform operations."""
        print("Welcome to the calculator!")
        print("Choose an operation:")
        print("1: Add")
        print("2: Subtract")
        print("3: Multiply")
        print("4: Divide")

        choice = input("Enter the number of the operation you want to perform (1/2/3/4): ")

        if choice in ['1', '2', '3', '4']:
            try:
                num1 = float(input("Enter the first number: "))
                num2 = float(input("Enter the second number: "))

                self.a = num1
                self.b = num2

            except ValueError:
                print("Invalid input! Please enter numbers only.")
                return

            if choice == '1':
                print(f"{num1} + {num2} = {self.add()}")

            elif choice == '2':
                print(f"{num1} - {num2} = {self.subtract()}")

            elif choice == '3':
                print(f"{num1} * {num2} = {self.multiply()}")

            elif choice == '4':
                result = self.divide()
                print(f"{num1} / {num2} = {result}")

        else:
            print("Invalid choice! Please select a valid operation (1/2/3/4).")


if __name__ == "__main__":
    calculator = Calculator(0, 0)
    calculator.calculator()