import json
from pathlib import Path

import pytest

from openfisca_core.tools import test_runner

PATH = Path(__file__).parent


def file_path(file_name):
    return PATH / f"./{file_name}"


def parse(function, file_name):
    with file_path(file_name).open("r") as file:
        return function(file.read())


def parse_json(file_name):
    return parse(json.loads, file_name)


def parse_yaml(file_name):
    return parse(test_runner.yaml.safe_load, file_name)


@pytest.fixture
def single():
    return parse_json("single.json")


@pytest.fixture
def couple():
    return parse_json("couple.json")


@pytest.fixture
def axes():
    return parse_yaml("axes.yaml")
