from datetime import datetime
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from routes.auth_routes import oauth_user_dependency
from routes.payment_routes import router as payment_router
from schema.order_schema import OrderCreateSchema, OrderUpdateSchema
from schema.user_schema import LoggedUser
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
    if not user:
        return RedirectResponse('/auth/login',
                                status_code=status.HTTP_303_SEE_OTHER)
    
    order_create_schema = OrderCreateSchema(
        user_id=str(user.id),
        date=datetime.now(),
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
    if not user:
        return RedirectResponse('/auth/login',
                                status_code=status.HTTP_303_SEE_OTHER)

    order = vm.get_by_id(order_id, str(user.id))

    return templates.TemplateResponse(
        'partials/order.html',
        {'request': request, **order.build_context(), 'editable': True}
    )


@router.put('/{order_id}')
def update_order(request: Request, order_id: int = 0,
                 comment: str = '', buyer_name: str = '',
                 buyer_phone: str = '', delivery_address: str = '',
                 date: datetime = datetime.now(),
                 user: LoggedUser | None = Depends(oauth_user_dependency),
                 vm: OrderViewModel = Depends(order_viewmodel_dependency),):
    if not user:
        return RedirectResponse('/auth/login',
                                status_code=status.HTTP_303_SEE_OTHER)

    order_update = OrderUpdateSchema(
        id=order_id,
        user_id=str(user.id),
        date=date,
        comment=comment,
        buyer_name=buyer_name,
        buyer_phone=buyer_phone,
        delivery_address=delivery_address
    )
    updated_order = vm.update_order(order_update)
    logger.info(f'Order updated: {updated_order}')

    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/order.html',
            {'request': request, 'user': user, **updated_order.build_context()}
        )

    return templates.TemplateResponse(
        'order.html',
        {'request': request, 'user': user, **updated_order.build_context()}
    )


@router.delete('/{order_id}/cancel')
def cancel_order(request: Request, order_id: int,
                 user: LoggedUser | None = Depends(oauth_user_dependency),
                 vm: OrderViewModel = Depends(order_viewmodel_dependency),):
    if not user:
        return RedirectResponse('/auth/login',
                                status_code=status.HTTP_303_SEE_OTHER)

    vm.remove_order(order_id=order_id, user_id=str(user.id))

    return templates.TemplateResponse(
        'empty.html',
        {'request': request, 'location': '/order/'}
    )


