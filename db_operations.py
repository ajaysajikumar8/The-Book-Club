
def get_books_by_author(author):
    books = db.session.query(Book).filter_by(author=author)
    return [book.title for book in books]