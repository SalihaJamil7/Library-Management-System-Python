import json
from datetime import datetime, timedelta
import os

BOOKS_FILE = "books.json"
USERS_FILE = "users.json"


# ---------------- FILE HANDLING ----------------

def load_data(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return default
    return default


def save_data(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# ---------------- INITIAL DATA ----------------

books = load_data("books.json", [
    {
        "id": "B001",
        "title": "Python Programming",
        "author": "John Smith",
        "available": True
    },
    {
        "id": "B002",
        "title": "Data Science Basics",
        "author": "Ali Khan",
        "available": True
    }
])

users = load_data("users.json", [])


# ---------------- USER FUNCTIONS ----------------

def register():
    print("\n===== MEMBER REGISTRATION =====")

    username = input("Enter username: ").strip()

    if not username:
        print("Username cannot be empty.")
        return

    for user in users:
        if user["username"].lower() == username.lower():
            print("Username already exists.")
            return

    password = input("Enter password: ").strip()

    if not password:
        print("Password cannot be empty.")
        return

    user = {
        "username": username,
        "password": password,
        "history": []
    }

    users.append(user)
    save_data(USERS_FILE, users)

    print("Registration successful!")


def login():
    print("\n===== MEMBER LOGIN =====")

    username = input("Username: ").strip()
    password = input("Password: ").strip()

    for user in users:
        if user["username"] == username and user["password"] == password:
            print(f"\nWelcome, {username}!")
            return user

    print("Invalid username or password.")
    return None


# ---------------- BOOK FUNCTIONS ----------------

def display_books():
    print("\n========== ALL BOOKS ==========")

    if not books:
        print("No books available.")
        return

    for book in books:
        status = "Available" if book["available"] else "Issued"

        print(f"""
Book ID    : {book['id']}
Title      : {book['title']}
Author     : {book['author']}
Status     : {status}
-------------------------------
""")


def add_book():
    print("\n===== ADD BOOK =====")

    book_id = input("Enter book ID: ").strip()

    for book in books:
        if book["id"] == book_id:
            print("Book ID already exists.")
            return

    title = input("Enter book title: ").strip()
    author = input("Enter author name: ").strip()

    if not title or not author:
        print("Title and author cannot be empty.")
        return

    new_book = {
        "id": book_id,
        "title": title,
        "author": author,
        "available": True
    }

    books.append(new_book)
    save_data(BOOKS_FILE, books)

    print("Book added successfully!")


def remove_book():
    print("\n===== REMOVE BOOK =====")

    book_id = input("Enter book ID: ").strip()

    for book in books:
        if book["id"] == book_id:

            if not book["available"]:
                print("This book is currently issued and cannot be removed.")
                return

            books.remove(book)
            save_data(BOOKS_FILE, books)

            print("Book removed successfully!")
            return

    print("Book not found.")


def search_book():
    print("\n===== SEARCH BOOK =====")

    keyword = input("Enter title, author or book ID: ").strip().lower()

    found = False

    for book in books:
        if (
            keyword in book["title"].lower()
            or keyword in book["author"].lower()
            or keyword == book["id"].lower()
        ):

            status = "Available" if book["available"] else "Issued"

            print(f"""
Book ID : {book['id']}
Title   : {book['title']}
Author  : {book['author']}
Status  : {status}
-------------------------------
""")

            found = True

    if not found:
        print("No matching book found.")


# ---------------- ISSUE BOOK ----------------

def issue_book(user):
    print("\n===== ISSUE BOOK =====")

    book_id = input("Enter book ID: ").strip()

    for book in books:

        if book["id"] == book_id:

            if not book["available"]:
                print("This book is already issued.")
                return

            issue_date = datetime.now()
            due_date = issue_date + timedelta(days=14)

            book["available"] = False

            transaction = {
                "book_id": book["id"],
                "title": book["title"],
                "issue_date": issue_date.strftime("%Y-%m-%d"),
                "due_date": due_date.strftime("%Y-%m-%d"),
                "return_date": None,
                "fine": 0
            }

            user["history"].append(transaction)

            save_data(BOOKS_FILE, books)
            save_data(USERS_FILE, users)

            print("\nBook issued successfully!")
            print("Issue Date:", issue_date.strftime("%Y-%m-%d"))
            print("Due Date  :", due_date.strftime("%Y-%m-%d"))

            return

    print("Book not found.")


# ---------------- RETURN BOOK ----------------

def return_book(user):
    print("\n===== RETURN BOOK =====")

    book_id = input("Enter book ID: ").strip()

    for book in books:

        if book["id"] == book_id:

            if book["available"]:
                print("This book is not currently issued.")
                return

            # Find active transaction
            transaction_found = None

            for transaction in user["history"]:
                if (
                    transaction["book_id"] == book_id
                    and transaction["return_date"] is None
                ):
                    transaction_found = transaction
                    break

            if transaction_found is None:
                print("This book was not issued to your account.")
                return

            return_date = datetime.now()
            due_date = datetime.strptime(
                transaction_found["due_date"],
                "%Y-%m-%d"
            )

            late_days = (return_date.date() - due_date.date()).days

            if late_days > 0:
                fine = late_days * 50
            else:
                fine = 0

            transaction_found["return_date"] = return_date.strftime(
                "%Y-%m-%d"
            )

            transaction_found["fine"] = fine

            book["available"] = True

            save_data(BOOKS_FILE, books)
            save_data(USERS_FILE, users)

            print("\nBook returned successfully!")

            if fine > 0:
                print("Late by:", late_days, "days")
                print("Fine: Rs.", fine)
            else:
                print("No fine. Thank you for returning on time!")

            return

    print("Book not found.")


# ---------------- HISTORY ----------------

def view_history(user):
    print("\n===== BORROWING HISTORY =====")

    if not user["history"]:
        print("You have no borrowing history.")
        return

    for transaction in user["history"]:

        status = (
            "Returned"
            if transaction["return_date"]
            else "Currently Issued"
        )

        print(f"""
Book       : {transaction['title']}
Book ID    : {transaction['book_id']}
Issue Date : {transaction['issue_date']}
Due Date   : {transaction['due_date']}
Return     : {transaction['return_date']}
Fine       : Rs. {transaction['fine']}
Status     : {status}
--------------------------------
""")


# ---------------- STATISTICS ----------------

def library_statistics():
    print("\n===== LIBRARY STATISTICS =====")

    total_books = len(books)

    available_books = 0
    issued_books = 0

    for book in books:
        if book["available"]:
            available_books += 1
        else:
            issued_books += 1

    print("Total Books     :", total_books)
    print("Available Books :", available_books)
    print("Issued Books    :", issued_books)
    print("Registered Users:", len(users))


# ---------------- ADMIN MENU ----------------

def admin_menu():

    while True:

        print("""
========== ADMIN MENU ==========

1. Add Book
2. Remove Book
3. Display Books
4. Search Book
5. Library Statistics
6. Logout
""")

        choice = input("Enter choice: ")

        if choice == "1":
            add_book()

        elif choice == "2":
            remove_book()

        elif choice == "3":
            display_books()

        elif choice == "4":
            search_book()

        elif choice == "5":
            library_statistics()

        elif choice == "6":
            print("Admin logged out.")
            break

        else:
            print("Invalid choice.")


# ---------------- USER MENU ----------------

def user_menu(user):

    while True:

        print(f"""
========== USER MENU ==========
Logged in as: {user['username']}

1. Display Books
2. Search Book
3. Issue Book
4. Return Book
5. Borrowing History
6. Logout
""")

        choice = input("Enter choice: ")

        if choice == "1":
            display_books()

        elif choice == "2":
            search_book()

        elif choice == "3":
            issue_book(user)

        elif choice == "4":
            return_book(user)

        elif choice == "5":
            view_history(user)

        elif choice == "6":
            print("Logged out successfully.")
            break

        else:
            print("Invalid choice.")


# ---------------- MAIN MENU ----------------

def main():

    while True:

        print("""
========================================
       LIBRARY MANAGEMENT SYSTEM
========================================

1. Admin Login
2. Member Registration
3. Member Login
4. Exit
""")

        choice = input("Enter your choice: ")

        if choice == "1":

            username = input("Admin Username: ")
            password = input("Admin Password: ")

            if username == "admin" and password == "admin123":
                print("Admin login successful!")
                admin_menu()
            else:
                print("Invalid admin credentials.")

        elif choice == "2":
            register()

        elif choice == "3":

            user = login()

            if user:
                user_menu(user)

        elif choice == "4":
            print("Thank you for using Library Management System!")
            break

        else:
            print("Invalid choice. Please try again.")


# ---------------- RUN PROGRAM ----------------

if __name__ == "__main__":
    main()