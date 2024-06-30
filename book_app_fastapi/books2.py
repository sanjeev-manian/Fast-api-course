from typing import Optional
from fastapi import Body, FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class Book:
    id: int
    name: str
    author: str
    rating: int

    def __init__(self, id, name, author, category, rating, published_date):
        self.id = id
        self.name = name
        self.author = author
        self.rating = rating
        self.category = category
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=3)
    author: str = Field(min_length=3, max_length=100)
    category: str = Field(min_length=3, max_length=100)
    rating: int = Field(gt=0, le=5)
    published_date: int


books: list[Book] = [
    Book(101, "ikigai", "ram", "self-help", 4, 2000),
    Book(102, "titanic", "sita", "adventure", 5, 2001),
    Book(103, "life of pi", "ram", "adventure", 5, 2001),
]


@app.get("/")
async def welcome():
    return {"message": "Welcome to library"}


@app.get("/books")
async def read_all_book():
    return books


@app.get("/books/{book_id}")
async def read_book_by_id(book_id: int = Path(gt=100)):
    for book in books:
        if book.id == int(book_id):
            return book


@app.get("/books/")
async def read_book_by_id(book_id: int = Query(gt=100)):
    for book in books:
        if book.id == int(book_id):
            return book
    raise HTTPException(status_code=404, detail="Item not found")


@app.post("/create_book", status_code=status.HTTP_201_CREATED)
async def create_book(new_book: BookRequest):
    validated_book = Book(**new_book.model_dump())
    new_book_id = books[-1].id + 1
    validated_book.id = new_book_id
    books.append(validated_book)


@app.put("/books/update_book/", status_code=status.HTTP_204_NO_CONTENT)
async def update_book_by_id(update_book: BookRequest):
    book_updated = False
    for i in range(len(books)):
        if books[i].id == update_book.id:
            books[i] = Book(**update_book.model_dump())
            book_updated = True
    if not book_updated:
        raise HTTPException(status_code=404, detail="Item not found")
