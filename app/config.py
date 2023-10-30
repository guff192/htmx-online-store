from pathlib import Path

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings


ROOT_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    # make this singleton for preventing multiple instances
    # see https://pydantic-docs.helpmanual.io/usage/settings/
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    debug: bool = Field(default=False, alias='DEBUG')

    host: str = Field(default='0.0.0.0', alias='HOST')
    port: int = Field(default=42069, alias='PORT')

    static_dir: Path = Field(default=ROOT_DIR / 'static', alias='STATIC_DIR')
    templates_dir: Path = Field(default=ROOT_DIR / 'templates', alias='TEMPLATES_DIR')
    db_url: str = Field(default='sqlite:///./db.sqlite3', alias='DB_URL')

    shop_name: str = Field(default='Shop name', alias='SHOP_NAME')

    # google settings
    google_oauth2_token_uri: str = Field(default='https://oauth2.googleapis.com/token', alias='GOOGLE_OAUTH2_TOKEN_URI')
    google_oauth2_client_id: str = Field(default='', alias='GOOGLE_OAUTH2_CLIENT_ID')


def log_settings():
    settings = Settings().model_dump()
    logger.debug(f'\n{"="*20} DEBUG MODE {"="*20}')
    logger.debug(settings)

