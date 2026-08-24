class BankAccount:
    def __init__(self,balance):
        self.balance=balance
        
    def deposit(self,amount):
        self.balance += amount
        print(f'Deposited {amount}. New balance: {self.balance}')

    def withdraw(self,amount):
        if amount < 0:
            print("Withdrawal amount cannot be negative")
        elif amount > self.balance:
            print("Insufficient funds")
        else:
            self.balance -= amount
            print(f'Withdrew {amount}. New balance: {self.balance}')

    def check_balance(self):
        print(f'Current balance: {self.balance}')

x=BankAccount(100)
x.deposit(50)
x.withdraw(30)
x.check_balance()

