from pytest import fixture

from tests.helpers.logging_helpers import log_test_info


@fixture(scope="package", autouse=True)
def log_repository_test_info():
    log_test_info("Testing Repository", level=1)

