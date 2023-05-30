from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    flash,
    abort,
    url_for,
)
from chat import get_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)
import json


app = Flask(__name__)
app.config["SECRET_KEY"] = "u}k@a5ThOTA5llx"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookclub.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()
db = SQLAlchemy(app=app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String(250), nullable=False)

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    author = db.Column(db.String(250), nullable=False)
    genre = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    img_url = db.Column(db.String(), nullable=False)


# CODE FOR ADDING MORE BOOKS TO DB

# with open("books.json", "r") as json_data:
#     books = json.load(json_data)

# for book in books["books"]:
#     book_title = book["title"]

#     if db.session.query(Book).filter_by(title = book_title).first():
#         print("book already exists")
#         continue

#     new_book = Book(
#         title = book["title"],
#         author = book["author"],
#         genre = book["genre"],
#         rating = book["rating"],
#         price = book["price"],
#         img_url = book["img_url"]
#     )
#     db.session.add(new_book)
#     db.session.commit()


# CODE FOR GETTING RETURNING BOOK TO USER
# def get_books_by_author(author):
#     books = db.session.query(Book).filter_by(author=author).all()
#     return [book.title for book in books]


@app.get("/")
def home():
    return render_template("index.html")


@app.route("/explore")
@login_required
def explore_books():
    bestselling_books = Book.query.order_by(Book.rating.desc()).limit(6).all()
    romance_books = Book.query.filter_by(genre="Romance").limit(6).all()
    fiction_books = Book.query.filter_by(genre="Fiction").limit(6).all()
    thriller_books = Book.query.filter_by(genre="Thriller").limit(6).all()
    scifi_books = Book.query.filter_by(genre="Sci-Fi").limit(6).all()
    return render_template(
        "explore.html",
        bestselling_books=bestselling_books,
        romance_books=romance_books,
        fiction_books=fiction_books,
        thriller_books=thriller_books,
        scifi_books=scifi_books,
    )


@app.route("/explore/books/<genre>")
@login_required
def explore_genre(genre):
    books = Book.query.filter_by(genre=genre).order_by(Book.rating.desc()).all()
    return render_template("genre.html", books=books)

@app.route("/explore/authors/<genre>")
@login_required
def explore_genre_authors(genre):
    books = Book.query.filter_by(genre=genre).order_by(Book.rating.desc()).all()
    authors = []
    for book in books:
        authors.append(book.author)
    return render_template("authors.html", authors=authors)


@app.route("/explore/book/<book>")
@login_required
def get_book(book):
    book_title = book
    book = Book.query.filter_by(title=book_title).first()
    return render_template("book.html", book=book)


@app.route("/explore/authors")
@login_required
def explore_authors():
    books = Book.query.order_by(Book.rating.desc()).all()
    authors = []
    for book in books:
        authors.append(book.author)
    
    authors = list(set(authors))
    return render_template("authors.html", authors=authors)


@app.route("/explore/authors/books/<author>")
@login_required
def explore_author_books(author):
    books = Book.query.filter_by(author=author).order_by(Book.rating.desc()).all()
    return render_template("author_books.html", books=books)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = db.session.query(User).filter_by(email=email).first()

        if user:
            if check_password_hash(pwhash=user.password, password=password):
                login_user(user)
                return redirect(url_for("explore_books"))
            else:
                flash("Password Incorrect, Please try again!")
                return redirect(url_for("login"))
        else:
            flash("This email does not exist. Please Try again")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if db.session.query(User).filter_by(email=request.form["email"]).first():
            flash("You have already signed up with that email. Login Instead")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(
            password=request.form["password"], method="pbkdf2:sha256", salt_length=8
        )
        new_user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=hashed_password,
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.post("/predict")
@login_required
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)


if __name__ == "__main__":
    app.run(debug=True)
