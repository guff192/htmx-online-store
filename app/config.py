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
    testing: bool = Field(default=False, alias='TESTING')

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
    shop_logo_name: str | None = Field(
        default=None,
        alias='SHOP_LOGO_NAME'
    )
    shop_public_url: Url = Field(default='', alias='SHOP_PUBLIC_URL')
    shop_email: str = Field(default='', alias='SHOP_EMAIL')

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

    # yandex oauth settings
    yandex_oauth2_token_uri: str = Field(
        default='https://login.yandex.ru/info?format=json',
        alias='YANDEX_OAUTH2_TOKEN_URI'
    )

    # avatar settings
    yandex_avatars_base_url: Url = Field(
        default='https://avatars.mds.yandex.net/get-yapic/',
        alias='YANDEX_AVATARS_BASE_URL'
    )
    yandex_avatars_default_size: str = Field(
        default='/islands-200',
        alias='YANDEX_AVATARS_DEFAULT_SIZE'
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

    # payment settings
    # tinkoff settings
    tinkoff_terminal_id: str = Field(default='', alias='TINKOFF_TERMINAL_ID')
    tinkoff_terminal_password: str = Field(
        default='',
        alias='TINKOFF_TERMINAL_PASSWORD'
    )

    # delivery settings
    # cdek settings
    cdek_base_api_url: Url = Field(
        default='https://api.edu.cdek.ru/v2',
        alias='CDEK_BASE_API_URL'
    ) 
    cdek_account: str = Field(
        default='wqGwiQx0gg8mLtiEKsUinjVSICCjtTEP',
        alias='CDEK_ACCOUNT'
    )
    cdek_secure_password: str = Field(
        default='RmAmgvSgSl1yirlz9QupbzOJVqhCxcP5',
        alias='CDEK_SECURE_PASSWORD'
    )
    cdek_shop_city_id: int = Field(
        default=44,
        alias='CDEK_SHOP_CITY_ID'
    )

    # phone verification settings
    # ucaller settings
    ucaller_service_id: str = Field(
        default='',
        alias='UCALLER_SERVICE_ID'
    )
    ucaller_service_secret_key: str = Field(
        default='',
        alias='UCALLER_SERVICE_SECRET_KEY'
    )


def log_settings():
    settings = Settings().model_dump()
    logger.debug(f'\n{"="*20} DEBUG MODE {"="*20}')

    settings_str = ''
    for k, v in settings.items():
        settings_str += f'{k}: {v}\n'
    logger.debug(f"Settings:\n{settings_str}")

