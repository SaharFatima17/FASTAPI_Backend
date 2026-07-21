from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user_model import Book

def seed_db():
    db = SessionLocal()
    # Check karein agar data pehle se hai
    if db.query(Book).count() > 0:
        print("Database already seeded!")
        return

    books = [
        Book(title="The Great Gatsby", author="F. Scott Fitzgerald", genre="Classic", total_copies=5, available_copies=5),
        Book(title="1984", author="George Orwell", genre="Dystopian", total_copies=3, available_copies=0), # Out of stock example
        Book(title="To Kill a Mockingbird", author="Harper Lee", genre="Classic", total_copies=2, available_copies=2),
        Book(title="The Hobbit", author="J.R.R. Tolkien", genre="Fantasy", total_copies=4, available_copies=4),
        # Aise hi aur 10-15 books add karein...
    ]
    
    db.add_all(books)
    db.commit()
    db.close()
    print("Seed complete! 15 books added.")

if __name__ == "__main__":
    seed_db()