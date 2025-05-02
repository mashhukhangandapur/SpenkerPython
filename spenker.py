expenses = []  # a list of dictionaries

# A function to take input from user to add his/her expense 
def add_expense():
    amount = float(input("Enter amount: "))
    category = input("Enter category: ")
    note = input("Enter note: ")
    date = input("Enter date (YYYY-MM-DD): ")

# Dictionary, containing details of an expense
    expense = {
        'amount': amount,
        'category': category,
        'note': note,
        'date': date
    }

# Appending the 
    expenses.append(expense)
    print("Expense added!")


def view_expenses():
    if not expenses:
        print("No expenses found.")
        return

    for idx, expense in enumerate(expenses):
        print(f"{idx+1}. ₹{expense['amount']} - {expense['category']} on {expense['date']} ({expense['note']})")

# This function will add the total amount of expenses 
# e.g. $100 + $70 = $170 .
def total_expense():
    total = sum(exp['amount'] for exp in expenses)
    print(f"Total expenses: ₹{total}")


# This function must be executed every time you run the program 
def menu():
    while True:
        print("\n--- Spenker Expense Tracker ---")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Total Expense")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            add_expense()
        elif choice == '2':
            view_expenses()
        elif choice == '3':
            total_expense()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

# Calling the above function

menu()

