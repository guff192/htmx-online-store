from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config import Settings
from db import init_db


settings = Settings()


@asynccontextmanager
async def lifecycle(app: FastAPI):
    init_db()

    yield



def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifecycle)

    return app


app = get_app()


def run(app: FastAPI | str = 'app.main:app') -> None:
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host, port=settings.port,
        reload=settings.debug
    )

if __name__ == '__main__':
    run()

