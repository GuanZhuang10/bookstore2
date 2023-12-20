import os
import sqlite3 as sqlite

parent_path = os.path.dirname(os.path.dirname(__file__))
book_db = os.path.join(parent_path, "book.db")
conn = sqlite.connect(book_db)

size = 0
start = 100
cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?", (size, start))
for row in cursor:
    book = Book()
    book.id = row[0]
    book.title = row[1]
    book.author = row[2]
    book.publisher = row[3]
    book.original_title = row[4]
    book.translator = row[5]
    book.pub_year = row[6]
    book.pages = row[7]
    book.price = row[8]

    book.currency_unit = row[9]
    book.binding = row[10]
    book.isbn = row[11]
    book.author_intro = row[12]
    book.book_intro = row[13]
    book.content = row[14]
    tags = row[15]

    picture = row[16]

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []