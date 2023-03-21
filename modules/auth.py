from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from database import Users, db

auth = Blueprint('auth', __name__, url_prefix="/civilERP/auth",
                 static_url_path="/civilERP")

login_manager = LoginManager()
login_manager.login_view = 'auth.sign_in'


@login_manager.user_loader
def user_loader(user_id):
    return Users.get(user_id)


@auth.route("/secure")
@login_required
def secure_link():
    return "Hey! see u are secured", 200


@auth.route("/", methods=["GET", "POST"])
def sign_in():
    errors = None

    if current_user.is_authenticated:
        return redirect(url_for('dash.dashboard'))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(email, password)
        user = Users.get_by_email(email)
        if user:
            if user.password == password:
                if user.is_authenticated:
                    login_user(user, remember=True)
                    return redirect(url_for('dash.dashboard'))
                else:
                    errors = "Contact administration to authenticate your account."
            else:
                errors = "Invalid email or password!"
        else:
            errors = "User doesn't exist"
    return render_template("views/authentication/sign-in.html", title="Sign In | C-Labs", errors=errors)


@auth.route("/create-account", methods=["GET", "POST"])
def create_account():
    errors = None
    messages = None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        print(name, email, password)
        if not Users.get_by_email(email):
            user = Users(name=name, email_address=email, password=password)
            db.session.add(user)
            db.session.commit()
            messages = "Account created successfully! Once admin authenticates you can access the dashboard."
        else:
            errors = "User already exists"

    return render_template("views/authentication/create-account.html", title="Join | C-Labs", errors=errors,
                           messages=messages)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.sign_in'))
