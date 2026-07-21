from sqlalchemy.orm import Session
from app.core.database import SessionLocal # Apne database session ka path check kar lein
from app.services.library_tools import (
    search_books, check_availability, borrow_book, 
    return_book, get_my_borrowed_books
)

# 1. Database session lo
db = SessionLocal()

print("--- Testing Library Tools ---")

# A. Search Test
print("\n1. Searching for 'Atomic':")
print(search_books(db, "Atomic"))

# B. Borrow Test (user_id=1, book_id=1)
print("\n2. Borrowing book ID 1:")
result = borrow_book(db, user_id=1, book_id=1)
print(result)

# C. Limit Check (Test: kya ye 3-book limit apply kar raha hai?)
# Agle 3 baar run karke check karein, 4th baar error aana chahiye
print("\n3. Current borrowed books:")
print(get_my_borrowed_books(db, user_id=1))

# D. Return Test
print("\n4. Returning book ID 1:")
print(return_book(db, user_id=1, book_id=1))

db.close()