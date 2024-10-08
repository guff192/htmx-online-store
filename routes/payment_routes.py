from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from exceptions.payment_exceptions import ErrUnsuccessfulPayment
from routes.auth_routes import oauth_user_dependency
from schema.order_schema import OrderUpdateSchema, TinkoffWebhookRequest
from schema.user_schema import LoggedUser
from viewmodels.delivery_viewmodel import DeliveryViewModel, delivery_viewmodel_dependency
from viewmodels.order_viewmodel import OrderViewModel, order_viewmodel_dependency
from viewmodels.payment_viewmodel import PaymentViewModel, payment_viewmodel_dependency
from viewmodels.user_viewmodel import UserViewModel, user_viewmodel_dependency


# router included in orders router
router = APIRouter(prefix='/payment', tags=['Payment'])
templates = Jinja2Templates(directory='templates')


@router.get('/{order_id}')
def get_payment_page(request: Request, order_id:  int,
                     user: LoggedUser | None = Depends(oauth_user_dependency),
                     vm: PaymentViewModel = Depends(payment_viewmodel_dependency)):
    if user is None:
        return RedirectResponse(f'/order/{order_id}/edit',
                                status_code=status.HTTP_303_SEE_OTHER)
        
    order_with_payment = vm.get_by_order_id(order_id, str(user.id))

    if request.headers.get('hx-request'):
        template_name = 'partials/payment.html'
    else:
        template_name = 'payment.html'

    response = templates.TemplateResponse(
        template_name,
        {'request': request, **order_with_payment.build_context(), 'user': user}
    )
    response.set_cookie('_payment_for_order', str(order_id), max_age=2592000,)

    return response


@router.post('/tinkoff')
async def handle_tinkoff_webhook(
    request: TinkoffWebhookRequest,
    vm: PaymentViewModel = Depends(payment_viewmodel_dependency),
    delivery_vm: DeliveryViewModel = Depends(delivery_viewmodel_dependency),
    order_vm: OrderViewModel = Depends(order_viewmodel_dependency),
    user_vm: UserViewModel = Depends(user_viewmodel_dependency),
):
    # Validate and process the request
    if not request.success:
        raise ErrUnsuccessfulPayment

    vm.update_payment_status(request)

    order = order_vm.get_by_id(int(request.order_id))
    user = user_vm.get_by_id(order.user_id)
    if not order.delivery_address.region.name:
        return 

    delivery_order_uuid = delivery_vm.create_delivery_order(
        order.id,
        order.delivery_address.city.code,
        order.delivery_address.address,
        order.buyer_name,
        order.buyer_phone,
        user.email,
        order.products
    )
    delivery_track_number = delivery_vm.get_cdek_order_number(order.id)
    # Update order with new delivery track number
    order_update = OrderUpdateSchema(
        id=order.id,
        user_id=order.user_id,
        date=order.date,
        comment=order.comment,
        buyer_name=order.buyer_name,
        delivery_address=order.delivery_address,
        buyer_phone=order.buyer_phone,
        delivery_track_number=delivery_track_number,
    )
    order_vm.update_order(order_update)

