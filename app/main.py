from contextlib import asynccontextmanager
import subprocess
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.admin import get_admin_app
from app.config import Settings, log_settings
from app.initial_setup import fetch_and_load_products
from db import init_db
from db.session import get_db
from middleware.auth_middleware import AdminMiddleware, LoginMiddleware
from routes.auth_routes import router as auth_router
from routes.cart_routes import router as cart_router
from routes.home_routes import router as home_router
from routes.product_routes import router as product_router
from services.auth_service import get_auth_service


settings = Settings()


@asynccontextmanager
async def lifecycle(app: FastAPI):
    '''
    Context manager for FastAPI app. It will run all code before `yield`
    on app startup, and will run code after `yield` on app shutdown.
    '''
    # initialize database (create all tables if they don't exist)
    init_db()
    fetch_and_load_products(get_db())

    # reload tailwindcss
    try:
        subprocess.run([
            'tailwindcss',
            '-i',
            str(settings.static_dir / 'src' / 'tw.css'),
            '-o',
            str(settings.static_dir / 'css' / 'main.css'),
        ])
    except Exception as e:
        print(f'Error running tailwindcss: {e}')

    # add loggers
    # LOGURU_AUTOINIT=False
    if settings.debug:
        logger.add(sys.stdout, level='DEBUG', colorize=True, format='[{time:HH:mm:ss}] <level>{level}</level> <cyan>{message}</cyan>')
        log_settings()

    yield


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifecycle)

    # ==========
    # Middleware
    # ==========
    # allow CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.add_middleware(AdminMiddleware, admin_path='/admin')

    app.add_middleware(LoginMiddleware, auth_service=get_auth_service())

    # ============
    # Mounted apps
    # ============
    app.mount('/admin', get_admin_app(), name='admin')

    app.mount('/static', StaticFiles(directory=settings.static_dir), name='static')

    # =======
    # Routers
    # =======
    app.include_router(auth_router)
    app.include_router(product_router)
    app.include_router(home_router)
    app.include_router(cart_router)

    return app


app = get_app()


def run(app: FastAPI | str = 'app.main:app') -> None:
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host, port=settings.port,
        reload=settings.debug,
        reload_includes=['*.html', '.env'],
        reload_dirs=[
            str(settings.templates_dir),
            str(settings.static_dir),
        ],
    )


if __name__ == '__main__':
    run()

