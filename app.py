from flask import Flask, render_template, request, jsonify, redirect, flash, abort, url_for
from chat import get_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user


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
    email = db.Column(db.String, nullable = False)
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




@app.get("/")
def home():
    return render_template("index.html")


@app.route("/explore")
@login_required
def explore_books():
    return render_template("explore.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]    
        password = request.form["password"]
        user = db.session.query(User).filter_by(email=email).first()
        
        if user:
            if check_password_hash(pwhash=user.password, password=password):
                login_user(user)
                return redirect(url_for('explore_books'))
            else:
                flash("Password Incorrect, Please try again!")
                return redirect(url_for('login'))
        else:
            flash("This email does not exist. Please Try again")
            return redirect(url_for('login'))
        
    return render_template("login.html" )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if db.session.query(User).filter_by(email=request.form["email"]).first():
            flash("You have already signed up with that email. Login Instead")
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(
            password=request.form["password"],
            method="pbkdf2:sha256",
            salt_length=8

        )
        new_user = User(
            name = request.form["name"],
            email = request.form["email"],
            password = hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.post("/predict")
@login_required
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)


if __name__ == "__main__":
    app.run(debug=True)


