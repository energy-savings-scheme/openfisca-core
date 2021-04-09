import pytest

from openfisca_core.entities import Entity, GroupEntity


@pytest.mark.usefixture("variable")
class TestEntity(Entity):

    def get_variable(self, variable_name, variable):
        result = variable(self)
        result.name = variable_name
        return result

    def check_variable_defined_for_entity(self, variable_name):
        return True


@pytest.mark.usefixture("variable")
class TestGroupEntity(GroupEntity):

    def get_variable(self, variable_name, variable):
        result = variable(self)
        result.name = variable_name
        return result

    def check_variable_defined_for_entity(self, variable_name):
        return True


@pytest.fixture(scope = "session")
def household_roles():
    return [
        {
            "key": "parent",
            "plural": "parents",
            "label": "Parents",
            "max": 2,
            "subroles": ["first_parent", "second_parent"],
            }, {
            "key": "child",
            "plural": "children",
            "label": "Child",
            },
        ]


@pytest.fixture(scope = "session")
def persons():
    return TestEntity("person", "persons", "", "")


@pytest.fixture(scope = "session")
def households(household_roles):
    return TestGroupEntity("household", "households", "", "", household_roles)
