import pytest

from openfisca_core import periods, tools
from openfisca_core.simulations import CycleError
from openfisca_core.variables import Variable


@pytest.fixture(scope = "module")
def variable_with_same_period1(persons):

    class test_variable_with_same_period1(Variable):
        value_type = int
        entity = persons
        definition_period = periods.MONTH

        def formula(person, period):
            variable = person(
                'test_variable_with_same_period2',
                period,
                )

            return variable

    return test_variable_with_same_period1


@pytest.fixture(scope = "module")
def variable_with_same_period2(persons):

    class test_variable_with_same_period2(Variable):
        value_type = int
        entity = persons
        definition_period = periods.MONTH

        def formula(person, period):
            variable = person(
                'test_variable_with_same_period1',
                period,
                )

            return variable

    return test_variable_with_same_period2


@pytest.fixture(scope = "module")
def variable_with_a_period_offset_1(persons):

    class test_variable_with_a_period_offset_1(Variable):
        value_type = int
        entity = persons
        definition_period = periods.MONTH

        def formula(person, period):
            variable = person(
                'test_variable_with_a_period_offset_2',
                period.last_month,
                )

            return variable

    return test_variable_with_a_period_offset_1


@pytest.fixture(scope = "module")
def variable_with_a_period_offset_2(persons):

    class test_variable_with_a_period_offset_2(Variable):
        value_type = int
        entity = persons
        definition_period = periods.MONTH

        def formula(person, period):
            variable = person(
                'test_variable_with_a_period_offset_1',
                period,
                )

            return variable

    return test_variable_with_a_period_offset_2


@pytest.fixture(scope = "module")
def variable_with_a_period_offset_3(persons):
    class test_variable_with_a_period_offset_3(Variable):
        value_type = int
        entity = persons
        definition_period = periods.MONTH

        def formula(person, period):
            variable = person(
                'test_variable_with_a_period_offset_4',
                period.last_month,
                )

            return 5 + variable

    return test_variable_with_a_period_offset_3


@pytest.fixture(scope = "module")
def variable_with_a_period_offset_4(persons):

    class test_variable_with_a_period_offset_4(Variable):
        value_type = int
        entity = persons
        definition_period = periods.MONTH

        def formula(person, period):
            variable = person(
                'test_variable_with_a_period_offset_3',
                period,
                )

            return 6 + variable

    return test_variable_with_a_period_offset_4


@pytest.fixture(scope = "module")
def variable_with_a_period_offset_5(persons):

    class test_variable_with_a_period_offset_5(Variable):
        value_type = int
        entity = persons
        definition_period = periods.MONTH

        def formula(person, period):
            variable = person(
                'test_variable_with_a_period_offset_3',
                period,
                )

            return 7 + variable

    return test_variable_with_a_period_offset_5


@pytest.fixture(scope = "module")
def cotisation(persons):

    class test_cotisation(Variable):
        """December cotisation depending on november value."""

        value_type = int
        entity = persons
        definition_period = periods.MONTH

        def formula(person, period):
            if period.start.month == 12:
                return 2 * person('test_cotisation', period.last_month)
            else:
                return person.empty_array() + 1

    return test_cotisation


@pytest.fixture(scope = "module")
def period(month):
    return periods.period(month)


@pytest.fixture(scope = "module", autouse = True)
def add_variables_to_tax_benefit_system(
        tax_benefit_system,
        variable_with_same_period1,
        variable_with_same_period2,
        variable_with_a_period_offset_1,
        variable_with_a_period_offset_2,
        variable_with_a_period_offset_3,
        variable_with_a_period_offset_4,
        variable_with_a_period_offset_5,
        cotisation,
        ):
    tax_benefit_system.add_variables(
        variable_with_same_period1,
        variable_with_same_period2,
        variable_with_a_period_offset_1,
        variable_with_a_period_offset_2,
        variable_with_a_period_offset_3,
        variable_with_a_period_offset_4,
        variable_with_a_period_offset_5,
        cotisation,
        )


@pytest.fixture
def simulation(simulation_builder, tax_benefit_system):
    return simulation_builder.build_default_simulation(tax_benefit_system)


def test_pure_cycle(simulation, period):
    with pytest.raises(CycleError):
        simulation.calculate(
            'test_variable_with_same_period1',
            period = period,
            )


def test_spirals_result_in_default_value(simulation, period):
    result = simulation.calculate(
        'test_variable_with_a_period_offset_1',
        period = period,
        )

    tools.assert_near(result, [0])


def test_spiral_heuristic(simulation, period):
    result1 = simulation.calculate(
        'test_variable_with_a_period_offset_3',
        period = period,
        )

    result2 = simulation.calculate(
        'test_variable_with_a_period_offset_4',
        period = period,
        )

    result3 = simulation.calculate(
        'test_variable_with_a_period_offset_4',
        period.last_month,
        )

    tools.assert_near(result1, [11])
    tools.assert_near(result2, [11])
    tools.assert_near(result3, [11])


def test_spiral_cache(simulation, period):
    result = simulation.calculate(
        'test_variable_with_a_period_offset_5',
        period = period,
        )

    cached = \
        simulation \
        .get_holder('test_variable_with_a_period_offset_5') \
        .get_array(period)

    assert result == cached


def test_cotisation_1_level(simulation, period):
    month = period.last_month
    cotisation = simulation.calculate('test_cotisation', period = month)
    tools.assert_near(cotisation, [0])
