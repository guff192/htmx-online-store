from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from schema.user_schema import UserBase
from viewmodels import DefaultViewModel, default_viewmodel_dependency


router = APIRouter(prefix='/cart', tags=['Cart'])
templates = Jinja2Templates(directory='templates')


@router.get('', dependencies=[])
def get_cart(
    request: Request,
    vm: DefaultViewModel = Depends(default_viewmodel_dependency),
):
    if request.headers.get('hx-request'):
        return templates.TemplateResponse(
            'partials/cart.html',
            context={'request': request, 'user': user})
    return templates.TemplateResponse(
        'cart.html',
        context={'request': request, 'user': user, **vm.build_context()}
    )

