from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from exceptions.product_photos_exceptions import ErrProductPhotoNotFound
from schema.product_schema import ProductPhotoPath, ProductPhotoSize
from viewmodels.product_viewmodel import (
    ProductViewModel, product_viewmodel_dependency
)


router = APIRouter(prefix='/photos', tags=['Photos'])
templates = Jinja2Templates(directory='templates')


@router.get('', response_class=HTMLResponse)
def get_one_photo(
    request: Request,
    file_name: str,
    path: str,
    product_vm: ProductViewModel = Depends(product_viewmodel_dependency),
):
    photo_path = ProductPhotoPath(file_name=file_name, path=path)
    photo_url = product_vm.get_photo_url(photo_path)

    context_data: dict[str, Any] = {'request': request}
    context_data.update(photo_urls=[photo_url])

    return templates.TemplateResponse(
        'partials/product_photos.html', context=context_data
    )


@router.get('/all', response_class=HTMLResponse)
def get_all_photos(
    request: Request,
    product_name: str,
    size: ProductPhotoSize = ProductPhotoSize.thumbs,
    product_vm: ProductViewModel = Depends(product_viewmodel_dependency),
):
    if not request.headers.get('hx-request'):
        return RedirectResponse('/products/catalog')

    main_photo_path = product_vm.get_main_photo(product_name, size)
    if not main_photo_path:
        raise ErrProductPhotoNotFound()

    photo_paths: list[ProductPhotoPath] = [main_photo_path]
    photo_paths += product_vm.get_all_photos_by_name(product_name, size)[1:]
    photo_urls = [product_vm.get_photo_url(photo_path)
                  for photo_path in photo_paths]

    context_data: dict[str, Any] = {'request': request}
    context_data.update(photo_urls=photo_urls)

    response = templates.TemplateResponse(
        'partials/product_photos.html', context=context_data
    )
    # Add response caching
    response.headers.update({'Cache-Control': 'max-age=86400, public'})

    return response


@router.get('/main', response_class=HTMLResponse)
def get_main_photo(
    request: Request,
    product_name: str,
    size: ProductPhotoSize = ProductPhotoSize.small,
    product_vm: ProductViewModel = Depends(product_viewmodel_dependency),
):
    if not request.headers.get('hx-request'):
        return RedirectResponse('/products/catalog')

    photo_path = product_vm.get_main_photo(product_name, size)
    if not photo_path:
        raise ErrProductPhotoNotFound()

    photo_url = product_vm.get_photo_url(photo_path)
    context_data: dict[str, Any] = {'request': request}
    context_data.update(photo_urls=[photo_url])

    # Add response caching
    response = templates.TemplateResponse(
        'partials/product_photos.html', context=context_data
    )
    response.headers.update({'Cache-Control': 'max-age=86400, public'})

    return response

