from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from schema.product_schema import (
    Product,
    ProductList,
    ProductUpdate,
    ProductUpdateResponse,
)
from services.product_service import ProductService, product_service_dependency
from viewmodels.product_viewmodel import ProductViewModel, product_viewmodel_dependency


router = APIRouter(prefix='/products', tags=['Products'])
templates = Jinja2Templates(directory='templates')


@router.get('', response_class=HTMLResponse)
def get_all_products(
        request: Request,
        product_vm: ProductViewModel = Depends(product_viewmodel_dependency)
    ):
    products_data: ProductList = product_vm.get_all()

    context_data: dict[str, Any] = {'request': request}
    context_data.update(products_data.build_context())

    if request.headers.get('hx-request'):
        return templates.TemplateResponse('partials/product_list.html', context=context_data)

    return templates.TemplateResponse('catalog.html', context=context_data)


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
        product_vm: ProductViewModel = Depends(product_viewmodel_dependency)):

    product = product_vm.get_by_id(product_id)
    if not product:
        return templates.TemplateResponse(
            '404.html',
            context={'request': request},
            status_code=404
        )

    context_data: dict[str, Any] = {'request': request}
    context_data.update(product.build_context())

    if request.headers.get('hx-request'):
        return templates.TemplateResponse('partials/product_detail.html', context=context_data)
    return templates.TemplateResponse('product.html', context=context_data)

