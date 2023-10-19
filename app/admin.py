from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import Session
from asgiref.wsgi import WsgiToAsgi
from starlette.types import ASGIApp
from db.session import get_db

from models.product import Product


def get_flask_app(session: Session = get_db()) -> ASGIApp:
    flask_app = Flask(__name__)
    flask_app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    flask_app.config['SECRET_KEY'] = 'secret_key'

    flask_admin = Admin(flask_app, url='/')
    flask_admin.add_view(ModelView(Product, session))

    return WsgiToAsgi(flask_app)

