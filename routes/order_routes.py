from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from exceptions.order_exceptions import ErrOrderInvalid
from routes.cookies import get_cart_from_cookies, get_order_from_cookies
from routes.auth_routes import oauth_user_dependency
from routes.payment_routes import router as payment_router
from schema.order_schema import (
    OrderCreateSchema, OrderInCookie, OrderUpdateSchema
)
from schema.user_schema import LoggedUser, UserCreate
from viewmodels.auth_viewmodel import AuthViewModel, auth_viewmodel_dependency
from viewmodels.order_viewmodel import OrderViewModel, order_viewmodel_dependency


router = APIRouter(prefix='/order', tags=['Order'])
router.include_router(payment_router)

templates = Jinja2Templates(directory='templates')


@router.post('/create_from_cart')
def create_order(
    request: Request,
    user: LoggedUser | None = Depends(oauth_user_dependency),
    vm: OrderViewModel = Depends(order_viewmodel_dependency),
):
    cookie_order_str: str = ''
    if not user:
        cookie_cart = get_cart_from_cookies(request.cookies)
        
        order = vm.create_from_cookie_cart(cookie_cart)
        cookie_order_str = order.cookie_str()
    else:
        order_create_schema = OrderCreateSchema(
            user_id=str(user.id),
            date=datetime.now(timezone.utc),
        )
        order = vm.create_order(order_create_schema)

    # generating context
    context = {'request': request, 'user': user, **order.build_context(),
             'editable': True}

    # choosing template
    if request.headers.get('hx-request'):
        template_name = 'partials/order.html'
    else:
        template_name = 'order.html'

    # creating response object
    response = templates.TemplateResponse(template_name, context)
    response.headers['Hx-Location'] = '{"path": ' +\
            f'"/order/{order.id}/edit", ' +\
            '"target": "#content"}'
    if cookie_order_str:
        response.set_cookie('_order', cookie_order_str, max_age=2592000,
                            samesite='strict')

    return response


@router.get('/{order_id}')
def get_order(request: Request, order_id: int,
    user: LoggedUser | None = Depends(oauth_user_dependency),
    vm: OrderViewModel = Depends(order_viewmodel_dependency),):
    if not user:
        return RedirectResponse('/auth/login',
                                status_code=status.HTTP_303_SEE_OTHER)

    order = vm.get_by_id(order_id, str(user.id))

    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/order.html',
            {'request': request, **order.build_context()}
        )

    return templates.TemplateResponse(
        'order.html',
        {'request': request, **order.build_context()}
    )


@router.get('/')
def get_user_orders(request: Request,
                    user: LoggedUser | None = Depends(oauth_user_dependency),
                    vm: OrderViewModel = Depends(order_viewmodel_dependency),):
    if not user:
        return RedirectResponse('/auth/login',
                                status_code=status.HTTP_303_SEE_OTHER)

    user_orders = vm.list_user_orders(str(user.id))
    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/user_orders.html',
            {'request': request, **user_orders.build_context()}
        )

    return templates.TemplateResponse(
        'user_orders.html',
        {'request': request, **user_orders.build_context()}
    )


@router.get('/{order_id}/edit')
def edit_order(request: Request, order_id: int,
                user: LoggedUser | None = Depends(oauth_user_dependency),
                vm: OrderViewModel = Depends(order_viewmodel_dependency)):
    cookie_order_str = ''
    if not user:
        order = get_order_from_cookies(request.cookies)
        logger.debug(f'Got order from cookies: {order}')
        if not order or not order_id == order.id:
            return RedirectResponse('/cart',
                                    status_code=status.HTTP_303_SEE_OTHER)
        cookie_order_str = order.cookie_str()
    else:
        order = vm.get_by_id(order_id, str(user.id))

    context = {'request': request, 'user': user,
               **order.build_context(), 'editable': True}
    if request.headers.get('hx-request'):
        template_name = 'partials/order.html'
    else:
        template_name = 'order.html'
    
    response = templates.TemplateResponse(template_name, context)
    if cookie_order_str:
        response.set_cookie('_order', cookie_order_str, max_age=2592000,
                            samesite='strict')

    return response


@router.put('/{order_id}')
def update_order(request: Request,
                 order_id: int = 0,
                 comment: str = '', buyer_name: str = '',
                 buyer_phone: str = '', delivery_address: str = '',
                 email: str = '',
                 user: LoggedUser | None = Depends(oauth_user_dependency),
                 vm: OrderViewModel = Depends(order_viewmodel_dependency),
                 auth_vm: AuthViewModel = Depends(auth_viewmodel_dependency),):
    user_token = ''
    if not user:
        if not all((email, buyer_name)):
            raise ErrOrderInvalid
        
        # Creating new user and getting its token for cookie
        user_create_schema = UserCreate(name=buyer_name, email=email)
        new_user = vm.create_user_for_order(user_create_schema)
        user_token = auth_vm.create_session({'sub': str(new_user.id)})

        order_update = OrderUpdateSchema(
            id=order_id, user_id=str(new_user.id),
            date=datetime.now(timezone.utc), comment=comment,
            buyer_name=buyer_name, buyer_phone=buyer_phone,
            delivery_address=delivery_address
        )
    else:
        order_update = OrderUpdateSchema(
            id=order_id, user_id=str(user.id),
            date=datetime.now(timezone.utc), comment=comment,
            buyer_name=buyer_name, buyer_phone=buyer_phone,
            delivery_address=delivery_address
        )

    updated_order = vm.update_order(order_update)

    # creating context and choosing template name
    context = {'request': request, 'user': user, **updated_order.build_context()}
    if request.headers.get('hx-request'):
        template_name = 'partials/order.html'
    else:
        template_name = 'order.html'

    # creating response
    response = templates.TemplateResponse(template_name, context)
    if user_token:
        response.set_cookie(
            key="_session", value=user_token, httponly=True, samesite="strict",
            secure=True, max_age=2592000,
        )

    return response


@router.delete('/{order_id}/cancel')
def cancel_order(request: Request, order_id: int,
                 user: LoggedUser | None = Depends(oauth_user_dependency),
                 vm: OrderViewModel = Depends(order_viewmodel_dependency),):
    if not user:
        cookie_order = get_order_from_cookies(request.cookies)
        if not cookie_order or not order_id == cookie_order.id:
            return RedirectResponse('/cart',
                                    status_code=status.HTTP_303_SEE_OTHER)

        vm.remove_order(order_id=order_id, user_id='')

        return templates.TemplateResponse(
            'empty.html',
            {'request': request, 'location': '/order/'}
        )

    vm.remove_order(order_id=order_id, user_id=str(user.id))

    return templates.TemplateResponse(
        'empty.html',
        {'request': request, 'location': '/order/'}
    )


