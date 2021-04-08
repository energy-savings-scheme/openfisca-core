import pytest

from openfisca_core.entities import Entity, GroupEntity

from tests.core.fixtures import variables


class TestEntity(Entity):
    def get_variable(self, variable_name):
        result = variables.TestVariable(self)
        result.name = variable_name
        return result

    def check_variable_defined_for_entity(self, variable_name):
        return True


class TestGroupEntity(GroupEntity):
    def get_variable(self, variable_name):
        result = variables.TestVariable(self)
        result.name = variable_name
        return result

    def check_variable_defined_for_entity(self, variable_name):
        return True


@pytest.fixture
def household_roles():
    return [{
        "key": "parent",
        "plural": "parents",
        "max": 2
        }, {
        "key": "child",
        "plural": "children",
        }]


@pytest.fixture
def persons():
    return TestEntity("person", "persons", "", "")


@pytest.fixture
def group_entity(household_roles):
    return TestGroupEntity("household", "households", "", "", household_roles)
