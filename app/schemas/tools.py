from pydantic import BaseModel

class SearchBooksArgs(BaseModel):
    query: str

class BookIdArgs(BaseModel):
    book_id: int

class BorrowReturnArgs(BaseModel):
    user_id: int
    book_id: int

class UserIdArgs(BaseModel):
    user_id: int