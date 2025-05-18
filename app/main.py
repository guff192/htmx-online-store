from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.admin import get_admin_app
from app.config import Settings, log_settings
from app.initial_setup import fetch_products, reload_tailwindcss, run_migrations
from db import init_db
from db.session import get_db
from middleware.auth_middleware import AdminMiddleware, LoginMiddleware
from routes.auth_routes import router as auth_router
from routes.cart_routes import router as cart_router
from routes.delivery_routes import router as delivery_router
from routes.home_routes import router as home_router
from routes.product_routes import router as product_router
from routes.product_photos_routes import router as product_photos_router
from routes.order_routes import router as order_router
from services.auth_service import get_auth_service


settings = Settings()


@asynccontextmanager
async def lifecycle(app: FastAPI):
    '''
    Context manager for FastAPI app. It will run all code before `yield`
    on app startup, and will run code after `yield` on app shutdown.
    '''
    # add loggers
    logger.remove()  # remove default logger
    if settings.testing:
        logger.add('app.test.log', level='DEBUG', colorize=True,
                   format='[{time:HH:mm:ss}] <level>{level}</level> <cyan>{message}</cyan>')
    elif settings.debug:
        logger.add('app.debug.log', level='DEBUG', colorize=True,
                   format='[{time:HH:mm:ss}] <level>{level}</level> <cyan>{message}</cyan>')
        log_settings()
    else:
        logger.add('app.log', level='INFO', colorize=True,
                   format='[{time:HH:mm:ss}] <level>{level}</level> <cyan>{message}</cyan>')
    logger.info('Logger initialized. Starting app...')

    # initialize database (create all tables if they don't exist)
    logger.info('Initializing database...')
    init_db()

    # run db migrations
    run_migrations()

    # logging access token for authenticating in debug mode
    if settings.debug:
        token = get_auth_service().create_access_token({'sub': '6fd6a87b-3ad3-4064-8f4b-cc76d33b1c4e'})
        logger.debug(f'{token = }')

    # fetching products from Google Spreadsheet
    if not settings.testing:
        fetch_products(get_db())

    # reload css styles
    reload_tailwindcss()

    yield


def get_app() -> FastAPI:
    logger.info('Creating FastAPI app...')
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
    app.mount('/admin', get_admin_app(get_db()), name='admin')

    app.mount('/static', StaticFiles(directory=settings.static_dir), name='static')

    # =======
    # Routers
    # =======
    app.include_router(auth_router)
    app.include_router(product_router)
    app.include_router(product_photos_router)
    app.include_router(home_router)
    app.include_router(cart_router)
    app.include_router(order_router)
    app.include_router(delivery_router)

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

