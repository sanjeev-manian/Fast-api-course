from fastapi import Body, FastAPI

app = FastAPI()

books = [
    {"id": 101, "name": "ikigai", "author": "ram", "category": "self-help"},
    {"id": 102, "name": "titanic", "author": "sita", "category": "adventure"},
    {"id": 103, "name": "life of pi", "author": "ram", "category": "adventure"},
]


@app.get("/")
async def fast_api():
    return {"message": "sanjeev"}


@app.get("/books")
async def read_all_books():
    return books


@app.get("/books/{book_title}")
async def read_all_books(book_title):
    for book in books:
        if book["name"] == book_title:
            return book


@app.get("/books/")
async def read_by_author(author: str):
    books_to_return = []
    for book in books:
        if book["author"].capitalize() == author.capitalize():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/category/")
async def get_all_books_by_category(category: str):
    books_to_return = []
    for book in books:
        if book["category"].capitalize() == category.capitalize():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{author}/")
async def read_by_author_and_category(author: str, category: str):
    books_to_return = []
    for book in books:
        if (
            book["author"].capitalize() == author.capitalize()
            and book["category"].capitalize() == category.capitalize()
        ):
            books_to_return.append(book)
    return books_to_return


@app.post("/books/create_book")
async def create_new_book(new_book=Body()):
    id = books[-1]["id"]
    new_book["id"] = id + 1
    books.append(new_book)


@app.put("/books/update_book")
async def update_book(updating_books=Body()):
    for i in range(len(books)):
        if books[i]["id"] == updating_books["id"]:
            books[i] = updating_books
            break


@app.delete("/books/delete_book/{book_id}")
async def update_book(book_id: int):
    for i in range(len(books)):
        if books[i]["id"] == book_id:
            del books[i]
            break
