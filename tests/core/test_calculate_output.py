import pytest

from openfisca_core import periods, simulations, tools
from openfisca_core.variables import Variable


@pytest.fixture(scope = "module")
def simple_variable(persons):

    class test_simple_variable(Variable):
        entity = persons
        definition_period = periods.MONTH
        value_type = int

    return test_simple_variable


@pytest.fixture(scope = "module")
def variable_with_calculate_output_add(persons):

    class test_variable_with_calculate_output_add(Variable):
        entity = persons
        definition_period = periods.MONTH
        value_type = int
        calculate_output = simulations.calculate_output_add

    return test_variable_with_calculate_output_add


@pytest.fixture(scope = "module")
def variable_with_calculate_output_divide(persons):

    class test_variable_with_calculate_output_divide(Variable):
        entity = persons
        definition_period = periods.YEAR
        value_type = int
        calculate_output = simulations.calculate_output_divide

    return test_variable_with_calculate_output_divide


@pytest.fixture(scope = "module", autouse = True)
def add_variables_to_tax_benefit_system(
        tax_benefit_system,
        simple_variable,
        variable_with_calculate_output_add,
        variable_with_calculate_output_divide,
        ):
    tax_benefit_system.add_variables(
        simple_variable,
        variable_with_calculate_output_add,
        variable_with_calculate_output_divide,
        )


@pytest.fixture
def simulation(simulation_builder, tax_benefit_system, single):
    return simulation_builder.build_from_entities(
        tax_benefit_system,
        single,
        )


def test_calculate_output_default(simulation, simple_variable, year):
    with pytest.raises(ValueError):
        simulation.calculate_output('test_simple_variable', year)


def test_calculate_output_add(simulation):
    simulation.set_input(
        'test_variable_with_calculate_output_add',
        '2017-01',
        [10],
        )

    simulation.set_input(
        'test_variable_with_calculate_output_add',
        '2017-05',
        [20],
        )

    simulation.set_input(
        'test_variable_with_calculate_output_add',
        '2017-12',
        [70],
        )

    tools.assert_near(
        simulation.calculate_output(
            'test_variable_with_calculate_output_add',
            2017,
            ),
        100,
        )


def test_calculate_output_divide(simulation):
    simulation.set_input(
        'test_variable_with_calculate_output_divide',
        2017,
        [12000],
        )

    tools.assert_near(
        simulation.calculate_output(
            'test_variable_with_calculate_output_divide',
            '2017-06',
            ),
        1000,
        )
