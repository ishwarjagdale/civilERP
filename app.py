from flask import Flask, redirect, url_for, Blueprint
from modules.auth import auth, login_manager
from modules.dashboard import dash
from database import db, Users

app = Flask(__name__, static_url_path='/civilERP')
app.config.from_pyfile('config.py')

civil_url = Blueprint('civilerp', __name__, url_prefix="/civilERP",
                      static_url_path="/civilERP")

with app.app_context():
    civil_url.register_blueprint(auth)
    civil_url.register_blueprint(dash)

    app.register_blueprint(civil_url)

    db.init_app(app)
    db.create_all()
    Users.create_super_user()

    login_manager.init_app(app)


@app.route("/civilERP")
def hello_world():
    return redirect(url_for('civilerp.auth.sign_in'))


if __name__ == '__main__':
    app.run()
