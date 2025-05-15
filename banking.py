# ----------------------------- #
#        Import Modules        #
# ----------------------------- #

import getpass
import datetime
import os
import random
import string

# ----------------------------- #
#        File Constants        #
# ----------------------------- #

ACCOUNTS_FILE = 'AccountDetails.txt'
TRANSACTION_FILE = 'transactions.txt'
CREDENTIALS_FILE = 'credentials.txt'
ACCOUNT_NUM_FILE = 'account_numbers.txt'

# ----------------------------- #
#        Global Variables      #
# ----------------------------- #

accounts = {}

# ----------------------------- #
#        File Operations       #
# ----------------------------- #

def load_data():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as accounts_file:
            for line in accounts_file:
                acc_no, name, balance = line.strip().split('|')
                accounts[acc_no] = {
                    'name': name,
                    'balance': float(balance),
                    'transactions': []
                }

    if os.path.exists(TRANSACTION_FILE):
        with open(TRANSACTION_FILE, 'r') as transaction_file:
            for line in transaction_file:
                acc_no, txn = line.strip().split('|', 1)
                if acc_no in accounts:
                    accounts[acc_no]['transactions'].append(txn)

def save_all_accounts():
    with open(ACCOUNTS_FILE, 'w') as accounts_file:
        for acc_no, details in accounts.items():
            accounts_file.write(f"{acc_no}|{details['name']}|{details['balance']}\n")

def write_transaction(acc_no, txn):
    with open(TRANSACTION_FILE, 'a') as transaction_file:
        transaction_file.write(acc_no + '|' + txn + '\n')

# ----------------------------- #
#        Generate Account Number #
# ----------------------------- #

def generate_account_number():
    if not os.path.exists(ACCOUNT_NUM_FILE):
        with open(ACCOUNT_NUM_FILE, 'w') as account_num_file:
            account_num_file.write('1001')  # Starting account number

    with open(ACCOUNT_NUM_FILE, 'r+') as account_num_file:
        try:
            current = int(account_num_file.read().strip())  # Read current number
        except ValueError:
            current = 1001  # Fallback if the file has corrupted data
        new = current + 1  # Increment account number

        account_num_file.seek(0)  # Go back to the start of the file
        account_num_file.write(str(new))  # Save the new number

        return f"AN{current}"  # Return account number with 'AN' prefix

def create_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def read_credentials():
    creds = {}
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as credentials_file:
            for line in credentials_file:
                if line.strip():
                    username, password, role = line.strip().split(':')
                    creds[username] = {'password': password, 'role': role}
    return creds

# ----------------------------- #
#        Account Actions       #
# ----------------------------- #

def create_account():
    name = input("Enter Your Full Name : ").strip().upper()
    if not name:
        print("Name cannot be empty.......")
        return

    try:
        balance = float(input("Enter Initial Balance: "))
        if balance < 0:
            print("Balance must be 0 or more.....")
            return
    except ValueError:
        print("Invalid input......")
        return

    acc_no = generate_account_number()  # Get the new account number with 'AN' prefix
    username = "user" + acc_no[2:]  # Example username format, removing 'AN' prefix
    password = create_password()

    with open(CREDENTIALS_FILE, 'a') as credentials_file:
        credentials_file.write(username + ':' + password + ':user\n')

    accounts[acc_no] = {
        'name': name,
        'balance': balance,
        'transactions': [f"Account opened with Rs.{balance} on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
    }

    save_all_accounts()
    write_transaction(acc_no, accounts[acc_no]['transactions'][0])

    print("\nAccount Created Successfully......")
    print("Account Number:", acc_no)
    print("Username:", username)
    print("Password:", password)

# ----------------------------- #
#         Deposit/Withdraw     #
# ----------------------------- #

def deposit_money():
    acc_no = input("Enter Account Number: ").strip()
    if acc_no not in accounts:
        print("Account not found.")
        return

    try:
        amount = float(input("Enter amount to deposit: "))
        if amount <= 0:
            print("Amount must be greater than 0.......")
            return
    except ValueError:
        print("Invalid input.......")
        return

    accounts[acc_no]['balance'] += amount
    txn = f"Deposited Rs.{amount} on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    accounts[acc_no]['transactions'].append(txn)
    write_transaction(acc_no, txn)
    save_all_accounts()
    print("Deposit Successful.......")

def withdraw_money():
    acc_no = input("Enter Account Number: ").strip()
    if acc_no not in accounts:
        print("Account not found.")
        return

    try:
        amount = float(input("Enter amount to withdraw: "))
        if amount <= 0:
            print("Invalid amount......")
            return
    except ValueError:
        print("Wrong input.....")
        return

    if amount > accounts[acc_no]['balance']:
        print("Not enough balance.......")
        return

    accounts[acc_no]['balance'] -= amount
    txn = f"Withdrew Rs.{amount} on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    accounts[acc_no]['transactions'].append(txn)
    write_transaction(acc_no, txn)
    save_all_accounts()
    print("Withdraw Successful!.....")

def check_balance():
    acc_no = input("Enter Account Number: ").strip()
    if acc_no not in accounts:
        print("Account not found.......")
        return
    print("Your Balance is Rs.", accounts[acc_no]['balance'])

def transaction_history():
    acc_no = input("Enter Account Number: ").strip()
    if acc_no not in accounts:
        print("Account not found.......")
        return

    print("Last 5 Transactions:")
    for t in accounts[acc_no]['transactions'][-5:]:
        print("-", t)


# ----------------------------- #
#         Admin Features       #
# ----------------------------- #

def update_account():
    acc_no = input("Enter your account number: ").strip()
    if acc_no not in accounts:
        print("Account not found.")
        return

    new_name = input("Enter new name: ").strip().upper()
    if not new_name:
        print("Name cannot be empty.")
        return

    old_name = accounts[acc_no]['name']
    accounts[acc_no]['name'] = new_name
    save_all_accounts()
    print(f"Name updated from {old_name} to {new_name}.")

def delete_account():
    acc_no = input("Enter account number to delete: ").strip()
    if acc_no not in accounts:
        print("Account not found.")
        return

    confirm = input(f"Are you sure you want to delete account {acc_no}? (yes/no): ").strip().lower()
    if confirm == 'yes':
        del accounts[acc_no]

        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'r') as credentials_file:
                lines = credentials_file.readlines()
            with open(CREDENTIALS_FILE, 'w') as credentials_file:
                for line in lines:
                    if f"user{acc_no}" not in line:
                        credentials_file.write(line)

        if os.path.exists(TRANSACTION_FILE):
            with open(TRANSACTION_FILE, 'r') as transaction_file:
                lines = transaction_file.readlines()
            with open(TRANSACTION_FILE, 'w') as transaction_file:
                for line in lines:
                    if not line.startswith(acc_no + '|'):
                        transaction_file.write(line)

        save_all_accounts()
        print(f"Account {acc_no} deleted successfully.")
    else:
        print("Deletion cancelled.")

# ----------------------------- #
#         Menu & Login         #
# ----------------------------- #

def admin_menu():
    while True:
        print("\nAdmin Menu")
        print("1. Create New Account")
        print("2. Delete Account")
        print("3. Update Account Name")
        print("4. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            create_account()
        elif choice == '2':
            delete_account()
        elif choice == '3':
            update_account()
        elif choice == '4':
            break
        else:
            print("Invalid option........")

def user_menu():
    while True:
        print("\nUser Menu")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Check Balance")
        print("4. View Transactions")
        print("5. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            deposit_money()
        elif choice == '2':
            withdraw_money()
        elif choice == '3':
            check_balance()
        elif choice == '4':
            transaction_history()
        elif choice == '5':
            break
        else:
            print("Invalid option.......")

def login(creds):
    if not creds:
        print("No credentials found. Please create an account.")
        create_new_user_credentials()
        return

    attempt = 0
    while attempt < 3:
        username = input("Enter username: ")
        password = getpass.getpass("Enter your password: ")

        if username in creds and creds[username]['password'] == password:
            role = creds[username]['role']
            print(f"Login successful! You are a {role}")
            if role == 'admin':
                admin_menu()
            elif role == 'user':
                user_menu()
            return
        else:
            print("Login failed. Wrong credentials.........")
            attempt += 1

    print("Your attempts are finished.....")

def create_new_user_credentials():
    role = input("Enter your role (admin/user): ").strip().lower()
    username = input("Enter your username: ").strip()
    password = getpass.getpass("Create a password: ").strip()

    with open(CREDENTIALS_FILE, 'a') as credentials_file:
        credentials_file.write(f"{username}:{password}:{role}\n")

    print(f"{role.capitalize()} credentials created successfully!")
    login(read_credentials())

# ----------------------------- #
#             Main             #
# ----------------------------- #

def main():
    load_data()
    creds = read_credentials()
    login(creds)

if __name__ == '__main__':
    main()
