from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from exceptions.auth_exceptions import ErrUnauthorized
from routes.auth_routes import oauth_user_dependency
from schema.user_schema import LoggedUser

from viewmodels.cart_viewmodel import CartViewModel, cart_viewmodel_dependency


router = APIRouter(prefix='/cart', tags=['Cart'])
templates = Jinja2Templates(directory='templates')


@router.get('', response_class=HTMLResponse, name='cart')
def get_cart(
    request: Request,
    user: LoggedUser | None = Depends(oauth_user_dependency),
    vm: CartViewModel = Depends(cart_viewmodel_dependency),
):
    if not user:
        return RedirectResponse('/auth/login', status_code=status.HTTP_303_SEE_OTHER)

    cart = vm.get_cart(str(user.id))
    context = {'request': request, 'user': user, **cart.build_context()}

    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/cart.html', context=context
        )

    return templates.TemplateResponse(
        'cart.html', context=context
    )



@router.get('/{product_id}', response_class=HTMLResponse)
def get_cart_info_for_product(
        request: Request,
        product_id: int,
        vm: CartViewModel = Depends(cart_viewmodel_dependency),
):
    user = request.state.user
    if not request.headers.get('hx-request') or not user:
        return RedirectResponse('/cart', status_code=status.HTTP_303_SEE_OTHER)
    

    product = vm.get_product_in_cart(str(user.id), product_id)

    response = templates.TemplateResponse(
        'partials/product_counter.html',
        {'request': request, 'user': user, **product.build_context()}
    )
    return response


@router.put('/add')
def add_to_cart(
    request: Request,
    product_id: int,
    configuration_id: int, 
    vm: CartViewModel = Depends(cart_viewmodel_dependency),
    user: LoggedUser | None = Depends(oauth_user_dependency),
):
    if not user:
        raise ErrUnauthorized()

    if not configuration_id:
        configuration_id = 0


    product_dict = (
        vm
        .add_to_cart(product_id=product_id, user_id=str(user.id),
                     configuration_id=configuration_id)
        .build_context()
    )
    context = {'request': request, 'user': user, **product_dict}

    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/product_counter.html', context=context
        )

    return RedirectResponse('/cart', status_code=status.HTTP_303_SEE_OTHER)


@router.put('/remove')
def remove_from_cart(
    request: Request,
    product_id: int,
    configuration_id: int,
    vm: CartViewModel = Depends(cart_viewmodel_dependency),
    user: LoggedUser | None = Depends(oauth_user_dependency),
):
    if not user:
        raise ErrUnauthorized()

    product_dict = (
        vm
        .remove_from_cart(product_id=product_id,
                          configuration_id=configuration_id,
                          user_id=str(user.id))
        .build_context()
    )
    context = {'request': request, 'user': user, **product_dict}

    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/product_counter.html', context=context
        )

    return RedirectResponse('/cart', status_code=status.HTTP_303_SEE_OTHER)

