from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from viewmodels import DefaultViewModel, default_viewmodel_dependency
from viewmodels.banner_viewmodel import BannerViewModel, banner_viewmodel_dependency
from viewmodels.product_viewmodel import(
    ProductViewModel,
    product_viewmodel_dependency
)


router = APIRouter(prefix='', tags=['Home'])
templates = Jinja2Templates(directory='templates')


@router.get('/')
def root():
    return RedirectResponse('/home', status_code=status.HTTP_301_MOVED_PERMANENTLY)


@router.delete('/remove_element', response_class=HTMLResponse, name='remove_element')
def remove_element():
    return HTMLResponse('', status_code=status.HTTP_200_OK)


@router.get('/home', response_class=HTMLResponse, name='home', dependencies=[])
def home(
    request: Request,
    offset: int = 0,
    # user: UserBase = Depends(google_oauth_user_dependency),
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
    products_vm: ProductViewModel = Depends(product_viewmodel_dependency),
    banner_vm: BannerViewModel = Depends(banner_viewmodel_dependency),
):
    product_list = products_vm.get_newcomers(offset=offset)
    banner_list = banner_vm.get_all()
    context_data: dict[str, Any] = {
        'request': request,
        **default_vm.build_context(),
        **product_list.build_context(),
        'banners': banner_list,
    }
    return templates.TemplateResponse('home.html', context=context_data)


@router.get('/about', response_class=HTMLResponse, name='about')
def about(
    request: Request,
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
):
    context_data: dict[str, Any] = {
        'request': request,
        **default_vm.build_context(),
    }
    return templates.TemplateResponse('partials/about.html', context=context_data)

