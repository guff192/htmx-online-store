from typing import Annotated, Any, Generator
 
from fastapi import APIRouter, Body, Cookie, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from schema.auth_schema import (
    GoogleLoginForm,
    GoogleOAuthCredentials,
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
    get_auth_viewmodel,
)
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
    credential = request.cookies.get("_session")
    if not credential:
        yield None
        return

    try:
        user: LoggedUser = auth_service.verify_session_token(credential)
    except Exception as e:
        logger.debug(f"Failed google authentication: {e}")
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


@router.post("/login/google")
def login_with_google_account(
    credential: Annotated[str, Form()],
    g_csrf_token: Annotated[str, Form()],
    cookie_csrf_token: str = Cookie(alias="g_csrf_token"),
    auth_vm: AuthViewModel = Depends(get_auth_viewmodel),
    user_vm: UserViewModel = Depends(get_user_viewmodel),
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

    response = RedirectResponse(
        "/auth/profile",
        status_code=status.HTTP_302_FOUND,
    )
    response.set_cookie(
        key="_session",
        value=token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=2592000,
    )
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
    access_token: Annotated[str, Body()],
    token_type: Annotated[str, Body()],
    expires_in: Annotated[int, Body()],
    auth_vm: AuthViewModel = Depends(get_auth_viewmodel),
    user_vm: UserViewModel = Depends(get_user_viewmodel),
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

    user: UserResponse | None = user_vm.get_by_email(email)
    if not user:
        user = user_vm.get_by_yandex_id_or_create(id_info)
    token = auth_vm.create_session({'sub': str(user.id)})

    response = Response(
        "Successfully authenticated with yandex ID!",
        status_code=status.HTTP_201_CREATED,
    )
    response.set_cookie(
        key="_session",
        value=token,
        httponly=True,
        samesite="strict",
        secure=True,
        max_age=2592000,
    )
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

