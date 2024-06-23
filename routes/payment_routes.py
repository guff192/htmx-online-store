from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from exceptions.payment_exceptions import ErrUnsuccessfulPayment
from routes.auth_routes import oauth_user_dependency
from schema.order_schema import TinkoffWebhookRequest
from schema.user_schema import LoggedUser
from viewmodels.payment_viewmodel import PaymentViewModel, payment_viewmodel_dependency


# router included in orders router
router = APIRouter(prefix='/payment', tags=['Payment'])
templates = Jinja2Templates(directory='templates')


@router.get('/{order_id}')
def get_payment_page(request: Request, order_id:  int,
                     user: LoggedUser | None = Depends(oauth_user_dependency),
                     vm: PaymentViewModel = Depends(payment_viewmodel_dependency)):
    if user is None:
        return RedirectResponse('/auth/login',
                                status_code=status.HTTP_303_SEE_OTHER)

    order_with_payment = vm.get_by_order_id(order_id, str(user.id))
    logger.debug(order_with_payment)

    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/payment.html',
            {'request': request,
             **order_with_payment.build_context(), 'user': user}
        )

    return templates.TemplateResponse(
        'payment.html',
        {'request': request,
         **order_with_payment.build_context(), 'user': user}
    )


@router.post('/tinkoff')
async def handle_tinkoff_webhook(
    request: TinkoffWebhookRequest,
    vm: PaymentViewModel = Depends(payment_viewmodel_dependency)
):
    # Validate and process the request
    if not request.success:
        raise ErrUnsuccessfulPayment

    vm.update_payment_status(request)

