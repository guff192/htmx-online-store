from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from viewmodels import DefaultViewModel, default_viewmodel_dependency


router = APIRouter(prefix='', tags=['Home'])
templates = Jinja2Templates(directory='templates')


@router.get('/')
def root():
    return RedirectResponse('/home', status_code=status.HTTP_301_MOVED_PERMANENTLY)


@router.get('/home', response_class=HTMLResponse, name='home', dependencies=[])
def home(
    request: Request,
    # user: UserBase = Depends(google_oauth_user_dependency),
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
):
    context_data: dict[str, Any] = {
        'request': request,
        # 'user': user,
        **default_vm.build_context(),
    }
    return templates.TemplateResponse('home.html', context=context_data)

