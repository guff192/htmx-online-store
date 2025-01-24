from app.config import Settings, log_settings

from tests.fixtures.logging_fixtures import setup_logger
from tests.helpers.logging_helpers import log_test_info


settings = Settings()


def test_logger():
    log_test_info("Testing Logger has been set up", level=0)
    if settings.debug:
        log_settings()

