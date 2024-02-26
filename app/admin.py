from fastapi import Request, Response
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse
from flask.app import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import Session
from starlette.middleware.base import (
    BaseHTTPMiddleware, RequestResponseEndpoint
)
from starlette.types import ASGIApp
from wtforms.fields import TextAreaField

from db.session import get_db
from models.banner import Banner
from models.product import Manufacturer, Product
from models.user import User, UserProduct
from schema.user_schema import UserBase
from services.auth_service import AuthService, get_auth_service
from viewmodels.user_viewmodel import UserViewModel, get_user_viewmodel


# ---------------------------------------------------------
# Model views for flask-admin
# ---------------------------------------------------------
class ProductModelView(ModelView):
    can_view_details = True
    can_edit = True
    can_delete = True
    can_create = True

    column_details_list: list[str] = [
        'name', 'price', 'count', 'newcomer', 'manufacturer'
    ]
    column_editable_list: list[str] = [
        'price', 'count', 'newcomer', 'manufacturer_id'
    ]
    column_searchable_list = ('name', 'manufacturer_id')

    form_columns: list[str] = [
        'name', 'description', 'price', 'manufacturer_id', 'newcomer',
    ]

    form_overrides = dict(
        description=TextAreaField,
        # manufacturer=SelectField
    )
    form_args = {
        'description': {
            'label': 'Description',
        },
        # 'manufacturer': {
        #     'label': 'Manufacturer',
        #     'choices': ([(m.name, m.id) for m in get_db().query(Manufacturer).all()]),
        # }
    }


class ManufacturerModelView(ModelView):
    can_view_details = True
    can_edit = True
    can_delete = True
    can_create = True

    column_editable_list: tuple[str] = ('name',)
    column_exclude_list: tuple[str] = ('products',)
    form_excluded_columns: tuple[str] = ('products',)


class UserModelView(ModelView):
    can_view_details = True
    can_edit = True
    can_delete = False
    can_create = False

    column_list: list[str] = ['id', 'name', 'is_admin']
    column_exclude_list: list[str] = ['google_id', 'profile_img_url']
    form_columns: list[str] = ['name', 'google_id', 'profile_img_url', 'is_admin']


class UserProductModelView(ModelView):
    can_view_details = True
    can_edit = True
    can_delete = True
    can_create = True

    column_list: list[str] = ['user.name', 'product.name', 'count']
    form_columns: list[str] = ['user_id', 'product_id', 'count']

    # form_overrides = dict(
    #     user=Select2Field,
    #     product=Select2Field,
    # )

    # form_args = {
    #     'user': {
    #         'label': 'User',
    #         'choices': ([(u.name, u.id) for u in get_db().query(User).all()]),
    #     },
    #     'product': {
    #         'label': 'Product',
    #         'choices': ([(p.name, p._id) for p in get_db().query(Product).all()]),
    #     },
    # }


class BannerModelView(ModelView):
    can_view_details = True
    can_edit = True
    can_delete = True
    can_create = True

    column_list: list[str] = ['name', 'img_url']
    column_editable_list: list[str] = ['img_url']


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------
class AdminMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        admin_path: str = '/admin',
        user_viewmodel: UserViewModel = get_user_viewmodel(),
        auth_service: AuthService = get_auth_service(),
    ) -> None:
        super().__init__(app)
        self.admin_path = admin_path
        self._vm = user_viewmodel
        self._service = auth_service

    def _check_admin(
        self,
        request: Request,
    ) -> bool:
        session_cookie = request.cookies.get('_session')
        if not session_cookie:
            return False

        user: UserBase = self._service.verify_session_token(session_cookie)

        if user.is_admin:
            return True
        return False

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        client, path = request.client, request.url.path

        if self.admin_path not in path:
            return await call_next(request)

        if not client or not client.host or not self._check_admin(request):
            return RedirectResponse('/')

        return await call_next(request)


# ---------------------------------------------------------
# Admin app function
# ---------------------------------------------------------
def get_admin_app(session: Session = get_db()) -> ASGIApp:
    flask_app = Flask(__name__)
    flask_app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    flask_app.config['SECRET_KEY'] = 'secret_key'

    flask_admin = Admin(flask_app, url='/')
    flask_admin.add_view(ProductModelView(Product, session))
    flask_admin.add_view(ManufacturerModelView(Manufacturer, session))
    flask_admin.add_view(UserModelView(User, session))
    flask_admin.add_view(UserProductModelView(UserProduct, session))
    flask_admin.add_view(BannerModelView(Banner, session))

    return WSGIMiddleware(flask_app)

