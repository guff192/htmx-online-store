from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from schema.product_schema import ProductList

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

