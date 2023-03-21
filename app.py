from flask import Flask, redirect, url_for
from modules.auth import auth, login_manager
from modules.dashboard import dash
from database import db, Users

app = Flask(__name__)
app.config.from_pyfile('config.py')

with app.app_context():
    app.register_blueprint(auth)
    app.register_blueprint(dash)

    db.init_app(app)
    db.create_all()
    Users.create_super_user()

    login_manager.init_app(app)


@app.route("/civilERP")
def hello_world():
    return redirect(url_for('auth.sign_in'))


if __name__ == '__main__':
    app.run()
