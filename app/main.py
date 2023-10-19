from contextlib import asynccontextmanager
import subprocess

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin import get_flask_app
from app.config import Settings
from db import init_db
from routes.home_routes import router as home_router
from routes.product_routes import router as product_router


settings = Settings()


@asynccontextmanager
async def lifecycle(app: FastAPI):
    '''
    Context manager for FastAPI app. It will run all code before `yield`
    on app startup, and will run code after `yeld` on app shutdown.
    '''
    # initialize database (create all tables if they don't exist)
    init_db()

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

    yield


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifecycle)

    app.mount('/admin', get_flask_app(), name='admin')
    app.mount('/static', StaticFiles(directory=settings.static_dir), name='static')

    # include all routers
    app.include_router(product_router)
    app.include_router(home_router)

    return app


app = get_app()


def run(app: FastAPI | str = 'app.main:app') -> None:
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host, port=settings.port,
        reload=settings.debug,
        reload_includes='*.html',
        reload_dirs=[str(settings.templates_dir), str(settings.static_dir)],
    )

if __name__ == '__main__':
    run()

