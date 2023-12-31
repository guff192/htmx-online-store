from loguru import logger
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from exceptions.auth_exceptions import ErrUnauthorized
from routes.auth_routes import google_oauth_user_dependency
from schema.user_schema import LoggedUser, UserBase

from viewmodels import DefaultViewModel, default_viewmodel_dependency
from viewmodels.cart_viewmodel import CartViewModel, cart_viewmodel_dependency


router = APIRouter(prefix='/cart', tags=['Cart'])
templates = Jinja2Templates(directory='templates')


@router.get('', response_class=HTMLResponse, name='cart')
def get_cart(
    request: Request,
    user: LoggedUser | None = Depends(google_oauth_user_dependency),
    vm: CartViewModel = Depends(cart_viewmodel_dependency),
):
    if not user:
        raise ErrUnauthorized()

    cart = vm.get_cart(str(user.id))
    context = {'request': request, 'user': user, **cart.build_context()}

    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/cart.html', context=context
        )

    return templates.TemplateResponse(
        'cart.html', context=context
    )


@router.post('/add')
def add_to_cart(
    request: Request,
    product_id: int,
    vm: CartViewModel = Depends(cart_viewmodel_dependency),
    user: LoggedUser | None = Depends(google_oauth_user_dependency),
):
    if not user:
        raise ErrUnauthorized()

    product_dict = (
        vm
        .add_to_cart(product_id=product_id, user_id=str(user.id))
        .build_context()
    )
    context = {'request': request, 'user': user, **product_dict}

    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/product_counter.html', context=context
        )

    return RedirectResponse('/cart', status_code=status.HTTP_303_SEE_OTHER)
