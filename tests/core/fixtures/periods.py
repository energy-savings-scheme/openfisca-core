import pytest


@pytest.fixture(scope = "session")
def year():
    return 2016


@pytest.fixture(scope = "session")
def month():
    return "2016-01"
