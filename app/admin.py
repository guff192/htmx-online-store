from fastapi import Request, Response
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse
from flask.app import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from loguru import logger
from sqlalchemy.orm import Session
from starlette.middleware.base import (
    BaseHTTPMiddleware, RequestResponseEndpoint
)
from starlette.types import ASGIApp
from wtforms.fields import TextAreaField

from db_models.banner import Banner
from db_models.order import Order
from db_models.payment import Payment
from db_models.product import AvailableProductConfigurationDbModel, ProductDbModel, ProductConfigurationDbModel
from db_models.manufacturer import Manufacturer
from db_models.user import UserDbModel, UserProductDbModel
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

    column_details_list: list[str] = ['name', 'price', 'count',
                                      'newcomer', 'manufacturer', 'resolution_name']

    column_editable_list: list[str] = ['price', 'count',
                                       'newcomer', 'manufacturer_id', 'resolution_name']

    column_searchable_list = ('name', 'manufacturer_id', 'resolution_name')

    form_columns: list[str] = ['name', 'description', 'price', 'manufacturer_id',
                               'newcomer', 'resolution', 'resolution_name', 'cpu',
                               'soldered_ram', 'can_add_ram', 'touch_screen']

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
    form_columns: list[str] = ['user_id', 'product_id', 'count', 'selected_configuration_id']
    column_details_list: list[str] = ['user.name', 'product.name', 'count', 'selected_configuration']

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


class ProductConfigurationModelView(ModelView):
    can_view_details = True
    can_edit = True
    can_delete = True
    can_create = True

    column_list: list[str] = ['id', 'ram_amount', 'ssd_amount', 'additional_price', 'is_default', 'additional_ram', 'soldered_ram']
    column_editable_list: list[str] = ['additional_price']

    column_searchable_list: list[str] = ['id']
    
    form_excluded_columns: tuple[str] = ('products',)


class AvailableProductConfigurationModelView(ModelView):
    can_view_details = True
    can_edit = True
    can_delete = True
    can_create = True

    column_list: list[str] = ['product.name', 'configuration.id']
    form_excluded_columns: list[str] = ['product', 'configuration']


class OrderModelView(ModelView):
    can_view_details = True
    can_edit = True
    can_delete = True
    can_create = True

    column_list: list[str] = ['id', 'user.email', 'buyer_name',
                              'date', 'payment.status']
    column_details_list: list[str] = ['id', 'user.name', 'date', 'buyer_name',
                                      'buyer_phone', 'region_name',
                                      'city_name', 'delivery_address']
    form_columns: list[str] = ['user_id', 'date', 'buyer_name', 'buyer_phone',
                               'delivery_address']
    column_editable_list: list[str] = ['user_id', 'date', 'buyer_name']

    column_default_sort: tuple[str, bool] = ('date', True)


class PaymentModelView(ModelView):
    can_view_details = True
    can_edit = True
    can_delete = False
    can_create = True

    column_list: list[str] = ['id', 'order_id', 'order.user.id', 'status']
    column_editable_list: list[str] = ['status']
    form_columns: list[str] = ['status', 'order_id']
    column_details_list: list[str] = ['id', 'order_id', 'order.user.email',
                                      'date', 'status']

    column_default_sort: tuple[str, bool] = ('date', True)


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
def get_admin_app(session: Session) -> ASGIApp:
    flask_app = Flask(__name__)
    flask_app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    flask_app.config['SECRET_KEY'] = 'secret_key'

    flask_admin = Admin(flask_app, url='/')
    flask_admin.add_view(ProductModelView(ProductDbModel, session))
    flask_admin.add_view(ManufacturerModelView(Manufacturer, session))
    flask_admin.add_view(UserModelView(UserDbModel, session))
    flask_admin.add_view(UserProductModelView(UserProductDbModel, session))
    flask_admin.add_view(BannerModelView(Banner, session))
    flask_admin.add_view(ProductConfigurationModelView(ProductConfigurationDbModel, session))
    flask_admin.add_view(AvailableProductConfigurationModelView(AvailableProductConfigurationDbModel, session))
    flask_admin.add_view(OrderModelView(Order, session))
    flask_admin.add_view(PaymentModelView(Payment, session))

    return WSGIMiddleware(flask_app)

