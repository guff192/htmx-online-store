from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel
from routes.auth_routes import oauth_user_dependency

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


@router.get('', response_class=HTMLResponse, name='product_list')
def get_product_list(
    request: Request,
    query: str = '',
    offset: int = 0,
    price_from: int = 0,
    price_to: int = 150000,
    ram: Annotated[list[int], Query()] = [],
    ssd: Annotated[list[int], Query()] = [],
    cpu: Annotated[list[str], Query()] = [],
    resolution: Annotated[list[str], Query()] = [],
    touchscreen: Annotated[list[bool], Query()] = [],
    graphics: Annotated[list[bool], Query()] = [],
    product_vm: ProductViewModel = Depends(product_viewmodel_dependency),
    user: LoggedUser | None = Depends(oauth_user_dependency),
):
    if not request.headers.get('hx-request'):
        return RedirectResponse('/products/catalog')

    products_data: ProductList = product_vm.get_all(
        query=query,
        offset=offset, user=user,
        price_from=price_from, price_to=price_to,
        ram=ram, ssd=ssd, cpu=cpu, resolution=resolution,
        touchscreen=touchscreen, graphics=graphics
    )

    filter_params_str = ''
    filter_params_str += f'query={query}&'
    filter_params_str += f'price_from={price_from}&price_to={price_to}&'
    filter_params_str += '&'.join('ram=' + str(r) for r in ram) + '&'
    filter_params_str += '&'.join('ssd=' + str(s) for s in ssd) + '&'
    filter_params_str += '&'.join('cpu=' + str(c) for c in cpu) + '&'
    filter_params_str += '&'.join('resolution=' + str(r) for r in resolution) + '&'
    filter_params_str += '&'.join('touchscreen=' + str(t) for t in touchscreen) + '&'
    filter_params_str += '&'.join('graphics=' + str(g) for g in graphics)

    context_data: dict[str, Any] = {'request': request}
    context_data.update(products_data.build_context())
    context_data.update(filter_params=filter_params_str)

    return templates.TemplateResponse(
        'partials/product_list.html',
        context=context_data
    )


@router.put('')
def update_product_by_name(
    product_update: ProductUpdate,
    product_service: ProductService = Depends(product_service_dependency),
) -> ProductUpdateResponse:
    updated_product_count = product_service.update_or_create_by_name(product_update)
    return updated_product_count


@router.get('/search', response_class=HTMLResponse)
def search(
    request: Request,
    query: str, offset: int = 0,
    product_vm: ProductViewModel = Depends(product_viewmodel_dependency),
):
    if not request.headers.get('hx-request'):
        return RedirectResponse('/products/catalog')

    products_data: ProductList = product_vm.search(query, offset)

    context_data: dict[str, Any] = {'request': request}
    context_data.update(products_data.build_context())

    return templates.TemplateResponse(
        'partials/product_list.html',
        context=context_data
    )


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


@router.get('/{product_id}/prices/{product_configuration_id}')
def get_product_prices(
    request: Request,
    product_id: int,
    product_configuration_id: int,
    product_vm: ProductViewModel = Depends(product_viewmodel_dependency)
):
    if not request.headers.get('hx-request'):
        return RedirectResponse(f'/products/{product_id}')

    prices = product_vm.get_product_prices(product_id,
                                           product_configuration_id)
    # building context
    prices_context = prices.build_context()

    setups = list(map(
        lambda c: {'ram': c.ram_amount, 'ssd': c.ssd_amount, 'id': c.id, 'name': c.__repr__()},
        prices_context['configurations']
    ))
    ram_amounts = list(set(map(lambda c: c.ram_amount, prices_context['configurations'])))
    ssd_amounts = list(set(map(lambda c: c.ssd_amount, prices_context['configurations'])))
    
    ram_configurations = []
    for i, amount in enumerate(ram_amounts):
        ram_configurations.append({'setups': [], 'ram': amount})
        for setup in setups:
            if amount == setup['ram']:
                ram_configurations[i]['setups'].append({
                    'id': setup['id'],
                    'name': setup['name'],
                    'ssd': setup['ssd']
                })
                
    ssd_configurations = []
    for i, amount in enumerate(ssd_amounts):
        ssd_configurations.append({'setups': [], 'ssd': amount})
        for setup in setups:
            if amount == setup['ssd']:
                ssd_configurations[i]['setups'].append({
                    'id': setup['id'],
                    'name': setup['name'],
                    'ram': setup['ram']
                })
                
    ram_configurations = sorted(ram_configurations, key=lambda c: c['ram'])
    ssd_configurations = sorted(ssd_configurations, key=lambda c: c['ssd'])
    prices_context['ram_configurations'] = ram_configurations
    prices_context['ssd_configurations'] = ssd_configurations

    return templates.TemplateResponse(
        'partials/price_configurator.html',
        context={'request': request, **prices.build_context()}
    )


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

