from typing import Annotated, Any, Mapping

from fastapi import APIRouter, Cookie, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from schema.user_schema import UserBase
from services.auth_service import GoogleOAuthService, google_oauth_service_dependency
from viewmodels import DefaultViewModel, default_viewmodel_dependency
from viewmodels.user_viewmodel import UserViewModel, user_viewmodel_dependency


router = APIRouter(prefix='/auth')
templates = Jinja2Templates(directory='templates')


#----------------------------------------------------
# Dependencies
#----------------------------------------------------
def google_oauth_user_dependency(
    request: Request,
    auth_service: GoogleOAuthService = Depends(google_oauth_service_dependency),
    user_vm: UserViewModel = Depends(user_viewmodel_dependency),
):
    credential = request.cookies.get('credential')
    if not credential:
        yield None
        return

    try:
        id_info = auth_service.verify_google_oauth2(credential)
    except Exception as e:
        logger.debug(f'Failed google authentication: {e}')
        yield None
        return
    
    user: UserBase = user_vm.get_by_google_id_or_create(id_info)

    yield user


@router.get('/login', response_class=HTMLResponse)
def get_login_page(
    request: Request,
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency)
):
    context_data: dict[str, Any] = {'request': request}
    context_data.update(default_vm.build_context())

    return templates.TemplateResponse('login.html', context=context_data)


GOOGLE_CLIENT_SECRET = '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'
# TODO: Move this to settings


@router.post('/login')
def process_login(
    credential: Annotated[str, Form()],
    g_csrf_token: Annotated[str, Form(title='g_csrf_token')],
    cookie_csrf_token: Annotated[str, Cookie(alias='g_csrf_token', title='g_csrf_token')],
    auth_service: GoogleOAuthService = Depends(google_oauth_service_dependency),
    user_vm: UserViewModel = Depends(user_viewmodel_dependency),
):

    id_info: Mapping[str, Any] = auth_service.verify_google_oauth2(credential, g_csrf_token, cookie_csrf_token)

    user: UserBase = user_vm.get_by_google_id_or_create(id_info)
    logger.debug(f'Logged in user: {user.name}')

    response = RedirectResponse(
        '/home',
        status_code=302,
    )
    response.set_cookie('credential', credential, httponly=True, samesite='strict')
    return response
    # TODO: Create profile template and redirect to it here


@router.post('/logout')
def process_logout():
    response = Response(
        headers={'hx-redirect': '/auth/login'},
    )
    response.delete_cookie('credential')
    return response

