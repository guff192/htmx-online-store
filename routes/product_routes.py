from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from schema.product_schema import ProductList

from viewmodels.product_viewmodel import ProductViewModel, get_product_viewmodel


router = APIRouter(prefix='/products', tags=['Products'])
templates = Jinja2Templates(directory='templates')


@router.get('/', response_class=HTMLResponse)
def get_all_products(
        request: Request,
        product_vm: ProductViewModel = Depends(get_product_viewmodel)
    ):
    products_data: ProductList = product_vm.get_all()

    if request.headers.get('hx-request'):
        context_data: dict[str, Any] = {'request': request}
        context_data.update(products_data.model_dump())
        return templates.TemplateResponse('products_list.html', context=context_data)

    return products_data

