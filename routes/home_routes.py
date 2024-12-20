from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi import status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.config import Settings
from routes.auth_routes import oauth_user_dependency
from schema.user_schema import LoggedUser
from viewmodels import DefaultViewModel, default_viewmodel_dependency
from viewmodels.banner_viewmodel import BannerViewModel, banner_viewmodel_dependency
from viewmodels.product_viewmodel import(
    ProductViewModel,
    product_viewmodel_dependency
)


router = APIRouter(prefix='', tags=['Home'])
templates = Jinja2Templates(directory='templates')

settings = Settings()


@router.get('/')
def root(request: Request):
    return RedirectResponse('/home', status_code=status.HTTP_301_MOVED_PERMANENTLY)


@router.delete('/remove_element', response_class=HTMLResponse, name='remove_element')
def remove_element():
    return HTMLResponse('', status_code=status.HTTP_200_OK)


@router.get('/home', response_class=HTMLResponse, name='home')
def home(
    request: Request,
    offset: int = 0,
    user: LoggedUser | None = Depends(oauth_user_dependency),
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
    products_vm: ProductViewModel = Depends(product_viewmodel_dependency),
    banner_vm: BannerViewModel = Depends(banner_viewmodel_dependency),
):
    products_schema = products_vm.get_newcomers(offset=offset)
    banners_schema = banner_vm.get_all()
    if not user:
        default_context = default_vm.build_context()
    else:
        default_context = default_vm.build_context_with_user(user)

    context_data: dict[str, Any] = {
        'request': request,
        **default_context,
        **products_schema.build_context(),
        **banners_schema.build_context(),
    }
    referer = request.headers.get('Referer', '')
    if str(settings.shop_public_url) not in referer:
        context_data.update(reload=True, location='/home')
    elif (paid_order_id := request.cookies.get('_payment_for_order', '')):
        response = RedirectResponse(f'/order/{paid_order_id}', status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie('_payment_for_order')
        return response

    try:
        response = templates.TemplateResponse('home.html', context=context_data)
        return response
    except Exception as e:
        logger.debug(f'Error while rendering home page: {e}')
        response = HTMLResponse('Error', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response


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


@router.get('/contacts', response_class=HTMLResponse, name='contacts')
def contacts(
    request: Request,
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
):
    context_data: dict[str, Any] = {
        'request': request,
        **default_vm.build_context(),
    }
    return templates.TemplateResponse('contacts.html', context=context_data)


@router.get('/help', response_class=HTMLResponse, name='help')
def help(
    request: Request,
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
):
    context_data: dict[str, Any] = {
        'request': request,
        **default_vm.build_context(),
    }
    return templates.TemplateResponse('help.html', context=context_data)


@router.get('/secret', response_class=HTMLResponse, name='secret')
def secret_page(
    request: Request,
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency),
):
    context_data: dict[str, Any] = {
        'request': request,
        **default_vm.build_context(),
    }
    return templates.TemplateResponse('secret.html', context=context_data)

