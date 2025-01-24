from loguru import logger

from app.config import log_settings

from tests.fixtures.logging_fixtures import setup_logger


def test_logger():
    logger.debug("Testing logger has been initialized")
    log_settings()
