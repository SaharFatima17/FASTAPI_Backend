from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.models.user_model import Book, Loan

def search_books(db: Session, query: str):
    books = db.query(Book).filter(Book.title.ilike(f"%{query}%") | Book.author.ilike(f"%{query}%")).all()
    return [{"id": b.id, "title": b.title, "author": b.author, "available": b.available_copies} for b in books]

def check_availability(db: Session, book_id: int):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book: return "Book not found."
    return {"title": book.title, "available": book.available_copies, "total": book.total_copies}

def borrow_book(db: Session, user_id: int, book_id: int):
    try:
        # Atomic Transaction shuru (Race condition rokne ke liye)
        with db.begin_nested():
            # with_for_update() row ko lock kar deta hai takay parallel requests ghalat result na dein
            book = db.query(Book).filter(Book.id == book_id).with_for_update().first()
            
            if not book:
                return {"success": False, "reason": "Book not found."}
            
            # Guardrail 1: 3-book limit check
            active_loans = db.query(Loan).filter(Loan.user_id == user_id, Loan.status == "borrowed").count()
            if active_loans >= 3:
                return {"success": False, "reason": "Limit reached: You cannot borrow more than 3 books."}
            
            # Guardrail 2: Availability check
            if book.available_copies <= 0:
                return {"success": False, "reason": "Book is currently unavailable."}
            
            # Action: Update stock and create loan
            book.available_copies -= 1
            new_loan = Loan(book_id=book_id, user_id=user_id, status="borrowed", due_date=datetime.now(timezone.utc) + timedelta(days=14))
            db.add(new_loan)
        
        db.commit() # Transaction confirm
        return {"success": True, "reason": f"Successfully borrowed '{book.title}'."}
        
    except Exception as e:
        db.rollback()
        return {"success": False, "reason": f"An error occurred: {str(e)}"}

def return_book(db: Session, user_id: int, book_id: int):
    try:
        with db.begin_nested():
            loan = db.query(Loan).filter(Loan.user_id == user_id, Loan.book_id == book_id, Loan.status == "borrowed").with_for_update().first()
            if not loan:
                return {"success": False, "reason": "Active loan record not found."}
            
            # Action
            loan.status = "returned"
            loan.returned_at = datetime.now(timezone.utc)
            book = db.query(Book).filter(Book.id == book_id).first()
            book.available_copies += 1
        
        db.commit()
        return {"success": True, "reason": f"Successfully returned '{book.title}'."}
        
    except Exception as e:
        db.rollback()
        return {"success": False, "reason": f"An error occurred: {str(e)}"}

def get_my_borrowed_books(db: Session, user_id: int):
    loans = db.query(Loan).filter(Loan.user_id == user_id, Loan.status == "borrowed").all()
    return [{"book_id": l.book_id, "due_date": l.due_date.strftime("%B %d, %Y")} for l in loans]