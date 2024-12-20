import re
from typing import Annotated, Any, Generator
 
from fastapi import APIRouter, Body, Cookie, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from routes.cookies import get_cart_from_cookies
from schema.auth_schema import (
    GoogleLoginForm,
    GoogleOAuthCredentials,
    PhoneLoginForm,
    YandexOauthCredentials
)
from schema.user_schema import LoggedUser, UserResponse, UserUpdate
from services.auth_service import (
    AuthService,
    auth_service_dependency,
)
from viewmodels import (
    DefaultViewModel,
    default_viewmodel_dependency
)
from viewmodels.auth_viewmodel import (
    AuthViewModel,
    auth_viewmodel_dependency,
    get_auth_viewmodel,
)
from viewmodels.cart_viewmodel import CartViewModel, cart_viewmodel_dependency
from viewmodels.user_viewmodel import (
    UserViewModel,
    get_user_viewmodel,
    user_viewmodel_dependency,
)
from exceptions.auth_exceptions import ErrWrongCredentials


router = APIRouter(prefix="/auth")
templates = Jinja2Templates(directory="templates")


# ----------------------------------------------------
# Dependencies
# ----------------------------------------------------
def oauth_user_dependency(
    request: Request,
    auth_service: AuthService = Depends(auth_service_dependency),
) -> Generator[LoggedUser | None, None, None]:
    """
    Dependency for FastAPI's DI system, yields the user that is making sthe request.
    """
    credential = request.cookies.get("_session")
    if not credential:
        yield None
        return

    try:
        user: LoggedUser = auth_service.verify_session_token(credential)
    except Exception as e:
        logger.debug(f"Failed authentication: {e}")
        yield None
        return

    yield user


# ----------------------------------------------------
# Routes
# ----------------------------------------------------
@router.get("/login", response_class=HTMLResponse)
def get_login_page(
    request: Request,
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
):
    context_data: dict[str, Any] = {"request": request}
    context_data.update(default_vm.build_context())

    return templates.TemplateResponse("login.html", context=context_data)


@router.get("/login/phone", response_class=HTMLResponse)
def get_phone_code_input(
    request: Request,
    phone: str,
    auth_vm: AuthViewModel = Depends(auth_viewmodel_dependency)
):
    phone = phone.strip()
    phone = ''.join(re.compile('([0-9]+)').findall(phone))
    form_data = PhoneLoginForm(phone=phone)
    form_data = auth_vm.get_phone_code_input(form_data)
    context_data: dict[str, Any] = {"request": request}
    context_data.update(form_data.build_context())

    return templates.TemplateResponse("partials/phone_code_input.html", context=context_data)


@router.post("/login/phone")
def process_phone_login(
    request: Request,
    phone: str,
    code: str,
    auth_vm: AuthViewModel = Depends(auth_viewmodel_dependency),
    user_vm: UserViewModel = Depends(user_viewmodel_dependency),
    cart_vm: CartViewModel = Depends(cart_viewmodel_dependency),
):
    form = PhoneLoginForm(phone=phone, code=code)

    form.phone = form.phone.strip()
    form.phone = ''.join(re.compile('([0-9]+)').findall(form.phone))
    if (form_verification_data := auth_vm.verify_phone_code(form)):
        logger.debug(form_verification_data)
        context_data: dict[str, Any] = {"request": request}
        context_data.update(form_verification_data.build_context())

        return templates.TemplateResponse(
            "partials/phone_code_input.html",
            context=context_data,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    user = user_vm.get_by_phone(form.phone)
    token = auth_vm.create_session({'phone': form.phone, 'sub': str(user.id)})

    cookie_cart = get_cart_from_cookies(request.cookies)
    for cart_product in cookie_cart.product_list:
        for _ in range(cart_product.count):
            cart_vm.add_to_cart(str(user.id), cart_product.product_id, cart_product.configuration_id)

    if 'cart' in request.headers.get('Hx-Current-URL', ''):
        redirect_url = '/cart'
    else:
        redirect_url = '/products/catalog'

    response = Response(
        status_code=status.HTTP_201_CREATED,
        headers={
            "Hx-Trigger": f'{{"redirect": "{redirect_url}"}}',
        },
    )
    response.set_cookie(
        key="_session",
        value=token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=86400000,
    )
    response.delete_cookie("_cart")
    return response


@router.post("/login/google")
def login_with_google_account(
    request: Request,
    credential: Annotated[str, Form()],
    g_csrf_token: Annotated[str, Form()],
    cookie_csrf_token: str = Cookie(alias="g_csrf_token"),
    auth_vm: AuthViewModel = Depends(get_auth_viewmodel),
    user_vm: UserViewModel = Depends(get_user_viewmodel),
    cart_vm: CartViewModel = Depends(cart_viewmodel_dependency),
):
    user_google_credential = GoogleOAuthCredentials(
        form_data=GoogleLoginForm(
            credential=credential,
            g_csrf_token=g_csrf_token,
        ),
        cookie_csrf_token=cookie_csrf_token
    )
    id_info = auth_vm.verify_oauth(user_google_credential)
    if not id_info:
        raise ErrWrongCredentials()

    user: UserResponse = user_vm.get_by_google_id_or_create(id_info)
    token = auth_vm.create_session({'sub': str(user.id)})

    cookie_cart = get_cart_from_cookies(request.cookies)
    for cart_product in cookie_cart.product_list:
        for _ in range(cart_product.count):
            cart_vm.add_to_cart(str(user.id), cart_product.product_id, cart_product.configuration_id)

    if 'cart' in request.headers.get('Referer', ''):
        redirect_url = '/cart'
    else:
        redirect_url = '/products/catalog'

    response = RedirectResponse(
        redirect_url,
        status_code=status.HTTP_302_FOUND,
    )
    response.set_cookie(
        key="_session",
        value=token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=86400000,
    )
    response.delete_cookie("_cart")
    return response
    # TODO: Create profile template and redirect to it here


@router.post("/login/tinkoff")
def login_with_tinkoff_account(
):
    pass


@router.get("/login/yandex")
def login_with_yandex_account(
    request: Request,
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
):
    # Data is in the form of
    # /auth/login/yandex#access_token=<access_token>&token_type=bearer&expires_in=<expires_in>

    context_data: dict[str, Any] = {
        "request": request,
        **default_vm.build_context(),
    }

    return templates.TemplateResponse(
        "yandex_auth.html",
        context=context_data
    )


@router.post("/login/yandex")
def process_yandex_login(
    request: Request,
    access_token: Annotated[str, Body()],
    token_type: Annotated[str, Body()],
    expires_in: Annotated[int, Body()],
    auth_vm: AuthViewModel = Depends(get_auth_viewmodel),
    user_vm: UserViewModel = Depends(get_user_viewmodel),
    cart_vm: CartViewModel = Depends(cart_viewmodel_dependency),
):
    yandex_credentials = YandexOauthCredentials(
        access_token=access_token, token_type=token_type, expires_in=expires_in
    )

    id_info = auth_vm.verify_oauth(yandex_credentials)
    if not id_info:
        raise ErrWrongCredentials()

    email: str = id_info.get('default_email', '')
    if not email:
        raise ErrWrongCredentials()

    user: UserResponse = user_vm.get_by_yandex_id_or_create(id_info)
    logger.debug(user)
    token = auth_vm.create_session({'sub': str(user.id)})

    cookie_cart = get_cart_from_cookies(request.cookies)
    for cart_product in cookie_cart.product_list:
        for _ in range(cart_product.count):
            cart_vm.add_to_cart(str(user.id), cart_product.product_id, cart_product.configuration_id)

    if 'cart' in request.headers.get('Hx-Current-URL', ''):
        redirect_url = '/cart'
    else:
        redirect_url = '/products/catalog'

    response = Response(
        status_code=status.HTTP_201_CREATED,
        headers={
            "Hx-Trigger": f'{{"redirect": "{redirect_url}"}}',
        },
    )
    response.set_cookie(
        key="_session",
        value=token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=86400000,
    )
    response.delete_cookie("_cart")
    return response


@router.get("/logout")
def process_logout():
    response = RedirectResponse("/auth/login")
    response.delete_cookie("_session")
    return response


@router.get('/profile')
def get_profile(
    request: Request,
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
    user: LoggedUser | None = Depends(oauth_user_dependency),
):
    if not user:
        return RedirectResponse("/auth/login")

    context = {'request': request, 'user': user, **default_vm.build_context()}
    if not request.headers.get('hx-request'):
        return templates.TemplateResponse('profile.html', context)

    return templates.TemplateResponse('partials/profile.html', context)


@router.get('/profile/edit')
def edit_profile(
    request: Request,
    user: LoggedUser | None = Depends(oauth_user_dependency),
):
    if not user:
        return RedirectResponse("/auth/login")

    if not request.headers.get('hx-request'):
        return RedirectResponse("/auth/profile")
    
    context = {'request': request, 'user': user}
    return templates.TemplateResponse('partials/profile_form.html', context)


@router.put('/profile/edit')
def update_user(
    request: Request,
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    user: LoggedUser | None = Depends(oauth_user_dependency),
    auth_vm: UserViewModel = Depends(user_viewmodel_dependency),
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
):
    if not user:
        return RedirectResponse("/auth/login")

    user_update_schema = UserUpdate(id=user.id, name=name, email=email)
    updated_user_response_schema = auth_vm.update(user_update_schema)

    context = {'request': request, 'user': updated_user_response_schema,
               **default_vm.build_context()}
    return templates.TemplateResponse('partials/profile.html', context)

