from loguru import logger
from pytest import fixture


@fixture(scope="session", autouse=True)
def setup_logger():
    logger.remove()
    logger.add('app.test.log', level='DEBUG', colorize=True,
        format='[{time:HH:mm:ss}] <level>{level}</level> <green>{function}</green> <cyan>{message}</cyan>')

