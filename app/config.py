from pathlib import Path

from loguru import logger
from pydantic import Field
from pydantic_core import Url
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
    templates_dir: Path = Field(
        default=ROOT_DIR / 'templates',
        alias='TEMPLATES_DIR'
    )

    db_url: str = Field(default='sqlite:///./db.sqlite3', alias='DB_URL')

    # JWT
    jwt_secret: str = Field(default='very strong secret', alias='JWT_SECRET')
    jwt_algorithm: str = Field(default='HS256', alias='JWT_ALGORITHM')

    # Shop settings
    shop_name: str = Field(default='Shop name', alias='SHOP_NAME')
    shop_public_url: Url = Field(default='', alias='SHOP_PUBLIC_URL')

    # google oauth settings
    google_oauth2_token_uri: str = Field(
        default='https://oauth2.googleapis.com/token',
        alias='GOOGLE_OAUTH2_TOKEN_URI'
    )
    google_oauth2_client_id: str = Field(
        default='',
        alias='GOOGLE_OAUTH2_CLIENT_ID'
    )
    google_client_secret: str = Field(
        default='',
        alias='GOOGLE_CLIENT_SECRET'
    )

    # Google spreadsheets settings
    posting_endpoint: str = Field(
        default='',
        alias='POSTING_ENDPOINT'
    )

    # storage settings
    # s3 settings
    aws_access_key_id: str = Field(default='', alias='AWS_ACCESS_KEY_ID')
    aws_secret_access_key: str = Field(
        default='',
        alias='AWS_SECRET_ACCESS_KEY'
    )

    # custom storage settings
    cloudflare_account_id: str = Field(default='', alias='CLOUDFLARE_ACCOUNT_ID')
    bucket_name: str = Field(default='', alias='BUCKET_NAME')
    public_bucket_url: Url = Field(default='', alias='PUBLIC_BUCKET_URL')


def log_settings():
    settings = Settings().model_dump()
    logger.debug(f'\n{"="*20} DEBUG MODE {"="*20}')
    logger.debug(settings)

