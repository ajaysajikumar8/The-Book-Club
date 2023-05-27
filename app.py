from flask import Flask, render_template, request, jsonify
from chat import get_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = "u}k@a5ThOTA5llx"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///bookclub.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app=app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(250), nullable = False)
    password = db.Column(db.String(250), nullable = False)



class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(250), nullable = False)
    author = db.Column(db.String(250), nullable = False)
    genre = db.Column(db.String(250), nullable = False)
    rating = db.Column(db.Float(), nullable=False)
    price = db.Column(db.Float(), nullable = False)
    img_url = db.Column(db.String(), nullable = False)


db.create_all()


@app.get("/")
def index_get():
    return render_template("index.html")


@app.route("/explore")
def explore_books():
    return render_template("explore.html")


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", form = form)


@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)


if __name__ == "__main__":
    app.run(debug=True)


