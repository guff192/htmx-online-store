from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from schema.auth_schema import GoogleLoginForm, GoogleOAuthCredentials
from schema.user_schema import UserBase
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
    get_auth_viewmodel
)
from viewmodels.user_viewmodel import (
    UserViewModel,
    get_user_viewmodel,
)
from exceptions.auth_exceptions import ErrWrongCredentials


router = APIRouter(prefix="/auth")
templates = Jinja2Templates(directory="templates")


# ----------------------------------------------------
# Dependencies
# ----------------------------------------------------
def google_oauth_user_dependency(
    request: Request,
    auth_service: AuthService = Depends(auth_service_dependency),
):
    credential = request.cookies.get("credential")
    if not credential:
        yield None
        return

    try:
        user: UserBase = auth_service.verify_session_credentials(credential)
    except Exception as e:
        logger.debug(f"Failed google authentication: {e}")
        yield None
        return

    yield user


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

    user: UserBase = user_vm.get_by_google_id_or_create(id_info)

    response = RedirectResponse(
        "/home",
        status_code=status.HTTP_302_FOUND,
    )
    response.set_cookie(
        key="credential",
        value=user_google_credential.form_data.credential,
        httponly=True,
        samesite="strict",
    )
    return response
    # TODO: Create profile template and redirect to it here


@router.post("/logout")
def process_logout():
    response = Response(
        headers={"hx-redirect": "/auth/login"},
    )
    response.delete_cookie("credential")
    return response
