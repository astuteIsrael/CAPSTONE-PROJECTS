import sqlite3
import random
import hashlib
import time

from datetime import datetime

from time import gmtime, strftime

from getpass import getpass



conn = sqlite3.connect("customers.db")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    age INTEGER NOT NULL,
    password TEXT NOT NULL,
    balance REAL DEFAULT 0,
    account_number TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transaction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT NOT NULL,
    transaction_amount REAL NOT NULL,
    balance_after REAL NOT NULL,
    transaction_time TEXT NOT NULL,
    FOREIGN KEY(username) REFERENCES customers(username)

)
""")

conn.commit()



def sign_up():

    print("-----------------------Sign Up-----------------------")

    while True:

        first_name = input("Enter your first name: ").strip()
        if not first_name:
            print("First name section cannot be left blank")
            continue
        break

    while True:
        last_name = input("Enter your last name: ").strip()

        if not last_name:
            print("Last name section cannot be left blank")
            continue
        break

    while True:
        username = input("Enter your username: ").strip()
        if not last_name:
            print("Last name section cannot be left blank")

        else:
            existing_username = cursor.execute("SELECT username FROM customers WHERE username = ?", (username,)).fetchone()
            if existing_username:
                print("this username already exists. Please choose a different one.")
            else:
                break

    while True:

        try:
            age = int(input("Enter your age: "))
            if age < 0:
                print("Your age can't be less than 0")
            else:
                break
                
        except ValueError:
            print("Age must be a number")



    while True:

        password = getpass("Enter your password: ").strip()
        
        if not password:
            print("Password field cannot be left blank")
            continue

        if len(password) < 8 or len(password) > 30:
            print("Password must be between 8 and 30 characters")
            continue

        if not any(char.islower() for char in password):
            print("Password must contain at least one lowercase")
            continue

        if not any(char.isupper() for char in password):
            print("Password must contain at least one uppercase")
            continue

        if not any(char.isdigit() for char in password):
            print("Password must contain at least one digit")
            continue

        if not any(char in "!@#$%^&*()_+[]{}|;:,.<>?/" for char in password):
            print("Password must contain at least one special character")
            continue



        confirm_password = getpass("Confirm your password: ").strip()
        
        if not confirm_password:
            print("Confirm Password field cannot be left blank")
            continue

        if password != confirm_password:
            print("Those passwords don't match")
            continue

        break

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    print("Password has been successfully created")

    full_name = f"{first_name} {last_name}"

    while True:
        account_number = str(random.randint(1000000000, 9999999999))
        existing_acctnumber = cursor.execute("SELECT account_number FROM customers WHERE account_number = ?", (account_number,)).fetchone()

        if not existing_acctnumber:
            break


    while True:

        try:
            deposit_amount = float(input("Enter the amount you want to deposit: "))
            # deposit = float(deposit_amount)
            if deposit_amount < 2000 or deposit_amount < 0:
                print(f"the initial deposit can not less than 2000 Naira neither can it be negative")
            else:
                balance = deposit_amount
                print(f"you have successfully deposited {deposit_amount} Naira")
                break
        except ValueError:
            print(f"Deposit amount must be a valid numeric value")
        

    try:
        cursor.execute("""
        INSERT INTO customers (full_name, username, age, password, balance, account_number) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, (full_name, username, age, hashed_password, balance, account_number))

    except sqlite3.IntegrityError as e:
        print(f"An error occurred: {e}")
    
    else:
        
        conn.commit()
        time.sleep(3)
        print("Sign Up was successful....Your account number is:", account_number)
        log_in()



def log_in():
    print("-----------------------Log In-----------------------")
    while True:
        username = input("Enter your username: ").strip()
        if not username:
            print("Username field cannot be left blank")
            continue
        break

    while True:
        password = getpass("Enter your password: ").strip()
        if not password:
            print("Password field cannot be left blank")
            continue
        break


    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # user = cursor.execute("""
    # SELECT first_name, username FROM customers WHERE username = ? AND password = ?
    # """, (username, hashed_password)).fetchone()


    user = cursor.execute("""
    SELECT full_name, username, balance, account_number FROM customers 
    WHERE username = ? AND password = ?
    """, (username, hashed_password)).fetchone()

    

    if user is None:
        print("The username or password you entered is invalid. Please try this again")
        return
    

    time.sleep(3)
    print("Log In Successful")
    operation_menu(user)
    

def account_details(user):
    full_name, username, balance, account_number = user

    print(f"welcome {full_name}...")

#     user = cursor.execute("""
#     SELECT account_number, full_name, username, balance
#     FROM customers
#     WHERE full_name = ?
# """, (full_name,)).fetchone()
    
    print(f"""
Account Details:
----------------------------
Full Name: {full_name}
Username: {username}
Account Number: {account_number}
Account Balance: {balance} Naira
----------------------------
""")




def deposit(user):
    full_name, username, balance, account_number = user

    while True:
        try:
            amount_deposited = int(input("Enter the amount you would like to deposit: "))
            if amount_deposited <= 0:
                print("Deposit amount must be a reasonable amount")
                continue
            break
        except ValueError:
            print("you have enter an actual figure")

    new_balance = balance + amount_deposited

    cursor.execute("""
    UPDATE customers
    SET balance = ?
    WHERE username = ?
    """, (new_balance, username))
    conn.commit()

    transaction_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    cursor.execute("""
    INSERT INTO transaction_history (username, transaction_type, transaction_amount, balance_after, transaction_time)
    VALUES (?, ?, ?, ?, ?)
    """, (username, "deposit", amount_deposited, new_balance, transaction_time))
    conn.commit()

    time.sleep(3)

    print(f"""
    ----------------------------------------------
    {full_name} you have deposited of {amount_deposited} Naira into this {account_number} successfully\n 
    Your new balance is {new_balance} Naira
    ----------------------------------------------
    """)
    





def withdrawal(user):
    full_name, username, balance, account_number = user

    while True:
        try:
            withdraw_amount = float(input("Please enter the amount of money you want to withdraw: ").strip())

            if withdraw_amount <= 0:
                print("Enter a valid amount as your withdrawal amount must be greater than 0")

            elif withdraw_amount > balance:
                print("Insufficient balance. You cannot withdraw more than your current balance")

            break

        except ValueError:
            print("you have entered is not a valid number")


    new_balance = balance - withdraw_amount

    cursor.execute("""
    UPDATE customers
    SET balance = ?
    WHERE username = ?
    """, (new_balance, username))
    conn.commit()

    transaction_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    cursor.execute("""
    INSERT INTO transaction_history (username, transaction_type, transaction_amount, balance_after, transaction_time)
    VALUES (?, ?, ?, ?, ?)
    """, (username, "withdraw", withdraw_amount, new_balance, transaction_time))
    conn.commit()

    time.sleep(3)
    print(f"{full_name} your withdrawal of {withdraw_amount} Naira from {account_number} was successful. Your new balance is {new_balance} Naira")





def available_balance(user):
    full_name, username, balance, account_number = user
    
    print(f"""
---------------------------------------------
"Welcome, {full_name}!"
"Your account number is {account_number}
"Your current balance is {balance:,.2f} Naira"
---------------------------------------------
""")
    
def transaction_history(user):
    full_name, username, _, _ = user


    cursor.execute("""
        SELECT transaction_type, transaction_amount, balance_after, transaction_time
        FROM transaction_history
        WHERE username = ?
        ORDER BY transaction_time DESC
""", (username,))
    
    transactions = cursor.fetchall()

    if not transactions:
        print("You have no transactions")
    else:
        print(f"Transaction History for {full_name}:")
        print("---------------------------------------------")
        print("Type\t\tAmount\t\tBalance After\t\tTime")
        print("---------------------------------------------")
        for transaction in transactions:
            transaction_type, transaction_amount, balance_after, transaction_time = transaction
            print(f"{transaction_type}\t{transaction_amount:,.2f} Naira\t{balance_after:,.2f} Naira\t\t{transaction_time}")




def transfer_funds(user):
    full_name, username, balance, account_number = user

    while True:
        recipient_account_number = input("Enter the recipient's account number: ").strip()
        if recipient_account_number == account_number:
            print("You cannot transfer money to your own account.")
        else:
            recipient = cursor.execute("""
            SELECT username, balance FROM customers WHERE account_number = ?
            """, (recipient_account_number,)).fetchone()
            if recipient:
                recipient_username, recipient_balance = recipient
                break
            else:
                print("Recipient account not found. Please try again.")

    while True:
        try:
            transfer_amount = float(input("Enter the amount you want to transfer: ").strip())
            if transfer_amount <= 0:
                print("Transfer amount must be greater than 0.")
            elif transfer_amount > balance:
                print("Insufficient balance. You cannot transfer more than your current balance.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    new_sender_balance = balance - transfer_amount
    new_recipient_balance = recipient_balance + transfer_amount

    cursor.execute("""
    UPDATE customers
    SET balance = ?
    WHERE username = ?
    """, (new_sender_balance, username))
    conn.commit()

    cursor.execute("""
    UPDATE customers
    SET balance = ?
    WHERE account_number = ?
    """, (new_recipient_balance, recipient_account_number))
    conn.commit()

    transaction_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    cursor.execute("""
    INSERT INTO transaction_history (username, transaction_type, transaction_amount, balance_after, transaction_time)
    VALUES (?, ?, ?, ?, ?)
    """, (username, "transfer_out", transfer_amount, new_sender_balance, transaction_time))
    conn.commit()

    cursor.execute("""
    INSERT INTO transaction_history (username, transaction_type, transaction_amount, balance_after, transaction_time)
    VALUES (?, ?, ?, ?, ?)
    """, (recipient_username, "transfer_in", transfer_amount, new_recipient_balance, transaction_time))
    conn.commit()

    print(f"{full_name} you have made the transfer of {transfer_amount} Naira to account {recipient_account_number} successfully")
    print(f"Your new balance is {new_sender_balance:,.2f} Naira")




def operation_menu(user):
    print("-----------------------Operation Menu-----------------------")
    time.sleep(3)
    print(f"Welcome to the operation menu page {user[0]}")


    while True:
        print("""
Operation Menu:
----------------------------
1. Make a deposit
2. Withdraw
3. Show my available balance
4. Transaction History
5. Transfer
6. Check your Account Details
7. Logout
----------------------------
        """)
    
        try:
            choice = int(input("Enter your choice (1-7): ").strip())
        except ValueError:
            print("Invalid input! Please enter a number between 1 and 7")
            continue

        if choice == 1:
            deposit(user)

        elif choice == 2:
            withdrawal(user)

        elif choice == 3:
            available_balance(user)

        elif choice == 4:
            transaction_history(user)

        elif choice == 5:
            transfer_funds(user)

        elif choice == 6:
            account_details(user)

        elif choice == 7:
            print("Logging out...")
            break
        else:
            print("Ohh dear! you have entered the wrong choice. Try again")




menu = """
-----------------------Menu-----------------------
1. Sign Up
2. Log In
3. Quit
"""


try:
    while True:
        print(menu)
        choice = input("Choose an option from the menu above: ").strip()

        if choice == "3":
            print("Thanks for shopping with us!")
            break

        if choice == "1":
            sign_up()
        elif choice == "2":
            log_in()
        else:
            print("Invalid choice, select from the menu")
            
except Exception as e:
    print(f"Oops! Something went wrong: {e}")
finally:
    conn.close()


def view_database():
    customers = cursor.execute("""
                   SELECT * FROM customers
                   """).fetchall()
    for customer in customers:
        print(customer)

data = view_database()
print(data)