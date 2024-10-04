from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from viewmodels.delivery_viewmodel import DeliveryViewModel, delivery_viewmodel_dependency
from viewmodels.order_viewmodel import OrderViewModel, order_viewmodel_dependency


router = APIRouter(prefix='/delivery', tags=['Delivery'])
templates = Jinja2Templates(directory='templates')


@router.get('/form', response_class=HTMLResponse)
def get_delivery_form(
    request: Request,
    vm: DeliveryViewModel = Depends(delivery_viewmodel_dependency)
):
    regions = vm.get_regions()
    return templates.TemplateResponse(
        'partials/delivery_form.html', {'request': request, 'regions': regions}
    )


@router.get('/cities', response_class=HTMLResponse)
def get_cities(
    request: Request,
    region: int,
    vm: DeliveryViewModel = Depends(delivery_viewmodel_dependency)
):
    cities = vm.get_cities(region)
    return templates.TemplateResponse(
        'partials/city_select.html', {'request': request, 'cities': cities}
    )


@router.get('/cost', response_class=HTMLResponse)
def get_shipping_cost(
    request: Request,
    city: int,
    products_count: int,
    order_id: int,
    vm: DeliveryViewModel = Depends(delivery_viewmodel_dependency),
    order_vm: OrderViewModel = Depends(order_viewmodel_dependency),

):
    cost = vm.get_shipping_cost(city, products_count)
    order_sum = order_vm.get_order_sum(order_id)
    cost += order_sum
    return templates.TemplateResponse(
        'partials/cost.html', {'request': request, 'cost': cost}
    )

