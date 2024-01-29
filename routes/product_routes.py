from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from routes.auth_routes import google_oauth_user_dependency

from schema.product_schema import (
    ProductList,
    ProductUpdate,
    ProductUpdateResponse,
)
from schema.user_schema import LoggedUser
from services.product_service import ProductService, product_service_dependency
from viewmodels import DefaultViewModel, default_viewmodel_dependency
from viewmodels.product_viewmodel import (
    ProductViewModel,
    product_viewmodel_dependency
)


router = APIRouter(prefix='/products', tags=['Products'])
templates = Jinja2Templates(directory='templates')


@router.get('/catalog', response_class=HTMLResponse, name='catalog')
def get_catalog(
    request: Request,
    default_vm: DefaultViewModel = Depends(default_viewmodel_dependency)
):
    context = default_vm.build_context()
    context.update({'request': request})

    return templates.TemplateResponse(
        'catalog.html',
        context=context
    )


@router.get('', response_class=HTMLResponse)
def get_product_list(
    request: Request,
    offset: int = 0,
    product_vm: ProductViewModel = Depends(product_viewmodel_dependency),
    user: LoggedUser | None = Depends(google_oauth_user_dependency),
):
    logger.debug(f'{request.state.user = }')
    if not request.headers.get('hx-request'):
        return RedirectResponse('/products/catalog')

    products_data: ProductList = product_vm.get_all(offset=offset, user=user)

    context_data: dict[str, Any] = {'request': request}
    context_data.update(products_data.build_context())

    return templates.TemplateResponse('partials/product_list.html', context=context_data)


@router.put('')
def update_product_by_name(
    product_update: ProductUpdate,
    product_service: ProductService = Depends(product_service_dependency),
) -> ProductUpdateResponse:
    logger.debug(product_update)
    updated_product_id = product_service.update_by_name(product_update)
    return updated_product_id


@router.get('/{product_id}', response_class=HTMLResponse)
def get_product_details(
    request: Request,
    product_id: int,
    product_vm: ProductViewModel = Depends(product_viewmodel_dependency)
):

    product = product_vm.get_by_id(product_id)

    context_data: dict[str, Any] = {'request': request}
    context_data.update(product.build_context())

    if request.headers.get('hx-request'):
        return templates.TemplateResponse('partials/product_detail.html', context=context_data)
    return templates.TemplateResponse('product.html', context=context_data)


@router.get('/{product_name}/photos', response_class=HTMLResponse)
def get_product_photos(
    request: Request,
    product_name: str,
    product_vm: ProductViewModel = Depends(product_viewmodel_dependency),
):
    if not request.headers.get('hx-request'):
        return RedirectResponse('/products/catalog')

    photo_links = [product_vm.get_photo_url(link)
                   for link in product_vm.get_all_photos_by_name(product_name)]

    context_data: dict[str, Any] = {'request': request}
    context_data.update(photo_urls=photo_links)

    return templates.TemplateResponse('partials/product_photos.html', context=context_data)

