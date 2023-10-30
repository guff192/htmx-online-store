from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from routes.auth_routes import google_oauth_user_dependency
from schema.user_schema import UserBase
from viewmodels.product_viewmodel import ProductViewModel, product_viewmodel_dependency


router = APIRouter(prefix='', tags=['Home'])
templates = Jinja2Templates(directory='templates')


@router.get('/')
def root():
    return RedirectResponse('/home', status_code=status.HTTP_301_MOVED_PERMANENTLY)


@router.get('/home', response_class=HTMLResponse, name='home', dependencies=[])
def home(
    request: Request,
    product_vm: ProductViewModel= Depends(product_viewmodel_dependency),
    user: UserBase = Depends(google_oauth_user_dependency),
):
    products = product_vm.get_all()
    context_data: dict[str, Any] = {
        'request': request,
        'user': user,
        **products.build_context()
    }
    return templates.TemplateResponse('home.html', context=context_data)

