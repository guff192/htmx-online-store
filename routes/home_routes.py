from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import status


router = APIRouter(prefix='', tags=['Home'])
templates = Jinja2Templates(directory='templates')


@router.get('/home', response_class=HTMLResponse, name='home')
def home(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})

@router.get('/')
def root(request: Request):
    return RedirectResponse('/home', status_code=status.HTTP_301_MOVED_PERMANENTLY)
