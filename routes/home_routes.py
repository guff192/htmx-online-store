from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from viewmodels import DefaultViewModel, default_viewmodel_dependency
from viewmodels.product_viewmodel import(
    ProductViewModel,
    product_viewmodel_dependency
)


router = APIRouter(prefix='', tags=['Home'])
templates = Jinja2Templates(directory='templates')


@router.get('/')
def root():
    return RedirectResponse('/home', status_code=status.HTTP_301_MOVED_PERMANENTLY)


@router.get('/home', response_class=HTMLResponse, name='home', dependencies=[])
def home(
    request: Request,
    offset: int = 0,
    # user: UserBase = Depends(google_oauth_user_dependency),
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
    products_vm: ProductViewModel = Depends(product_viewmodel_dependency),
):
    product_list = products_vm.get_newcomers(offset=offset)
    context_data: dict[str, Any] = {
        'request': request,
        **default_vm.build_context(),
        **product_list.build_context(),
    }
    logger.debug(context_data)
    return templates.TemplateResponse('home.html', context=context_data)

