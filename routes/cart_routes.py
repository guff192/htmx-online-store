from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from routes.cookies import add_product_to_cookie_cart, get_cart_from_cookies, remove_product_from_cookie_cart
from routes.auth_routes import oauth_user_dependency
from schema import SchemaUtils
from schema.cart_schema import CartInCookie
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
    if user:
        cart = vm.get_cart(str(user.id))
        context_data = {'request': request, 'user': user, **cart.build_context()}
    else:
        cart_cookie_str = request.cookies.get("_cart")
        if cart_cookie_str:
            cart = CartInCookie.model_validate_json(cart_cookie_str)
        else:
            cart = CartInCookie(product_list=[])

        schema_utils = SchemaUtils()
        products = vm.from_cookie(cart)

        @schema_utils.add_shop_to_context
        @schema_utils.add_debug_info_to_context
        def context_func():
            return {'request': request, 'product_list': products}  

        context_data = context_func()

    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/cart.html', context=context_data
        )

    return templates.TemplateResponse(
        'cart.html', context=context_data
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
    if not request.headers.get('hx-request'):
        response = RedirectResponse(
            '/cart', status_code=status.HTTP_303_SEE_OTHER
        )

    cookie_cart_str = ''

    if user:
        product = vm.add_to_cart(
            product_id=product_id, user_id=str(user.id),
            configuration_id=configuration_id
        )
    else:
        cookie_cart = get_cart_from_cookies(request.cookies)
        cookie_cart = add_product_to_cookie_cart(
            cookie_cart, product_id, configuration_id
        )
        product = cookie_cart.product_list[-1]

        cookie_cart_str = cookie_cart.cookie_str()

    # creating response
    context = {'request': request, 'user': user, **product.build_context()}
    response = templates.TemplateResponse(
        'partials/product_counter.html', context=context
    )

    # setting updated cart in cookie
    if cookie_cart_str:
        response.set_cookie(
            key='_cart',
            value=cookie_cart_str,
            max_age=2592000,
            samesite='strict',
        )

    return response


@router.put('/remove')
def remove_from_cart(
    request: Request,
    product_id: int,
    configuration_id: int,
    vm: CartViewModel = Depends(cart_viewmodel_dependency),
    user: LoggedUser | None = Depends(oauth_user_dependency),
):
    cookie_cart_str = ''
    if  user:
        product = vm.remove_from_cart(
            product_id=product_id, configuration_id=configuration_id,
            user_id=str(user.id)
        )
    else:
        # getting cart from cookie
        cookie_cart = get_cart_from_cookies(request.cookies)

        # removing product from cookie cart object
        cookie_cart = remove_product_from_cookie_cart(
            cookie_cart, product_id, configuration_id
        )

        # always have last product here, as we keep it anyway in product_list
        product = cookie_cart.product_list[-1] 

        # creating new string to set cart in cookies
        if product.count != 0 or len(cookie_cart.product_list) > 1:
            cookie_cart_str = cookie_cart.cookie_str()
        else:
            cookie_cart_str = '{"product_list": []}'
    
    # creating response
    context = {'request': request, 'user': user, **product.build_context()}
    if not request.headers.get('hx-request'):
        response = RedirectResponse('/cart', status_code=status.HTTP_303_SEE_OTHER)
    else:
        response = templates.TemplateResponse(
            'partials/product_counter.html', context=context
        )
    
    # setting updated cart in cookie
    if cookie_cart_str:
        response.set_cookie(
            key='_cart',
            value=cookie_cart_str,
            max_age=2592000,
            samesite='strict',
        )

    return response
        


