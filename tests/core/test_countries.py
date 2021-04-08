import pytest

from openfisca_country_template import CountryTaxBenefitSystem

from openfisca_core import periods, populations, tools
from openfisca_core.errors import VariableNameConflictError, VariableNotFoundError
from openfisca_core.variables import Variable


@pytest.fixture
def isolated_tax_benefit_system():
    return CountryTaxBenefitSystem()


@pytest.fixture
def make_simulation(simulation_builder, tax_benefit_system):

    def _make_simulation(period, variables):
        simulation_builder.set_default_period(period)

        return simulation_builder.build_from_variables(
            tax_benefit_system,
            variables,
            )

    return _make_simulation


@pytest.fixture
def make_isolated_simulation(simulation_builder):

    def _make_simulation(tax_benefit_system, period, variables):
        simulation_builder.set_default_period(period)

        return simulation_builder.build_from_variables(
            tax_benefit_system,
            variables,
            )

    return _make_simulation


def test_input_variable(make_simulation, month):
    simulation = make_simulation(month, {'salary': 2000})
    tools.assert_near(simulation.calculate('salary', month), [2000], absolute_error_margin = 0.01)


def test_basic_calculation(make_simulation, month):
    simulation = make_simulation(month, {'salary': 2000})
    tools.assert_near(simulation.calculate('income_tax', month), [300], absolute_error_margin = 0.01)


def test_calculate_add(make_simulation, month):
    simulation = make_simulation(month, {'salary': 24000})
    tools.assert_near(simulation.calculate_add('income_tax', month), [3600], absolute_error_margin = 0.01)


def test_calculate_divide(make_simulation, month):
    simulation = make_simulation(month, {
        'accommodation_size': 100,
        'housing_occupancy_status': 'tenant',
        })
    tools.assert_near(simulation.calculate_divide('housing_tax', month), [1000 / 12.], absolute_error_margin = 0.01)


def test_bareme(make_simulation, month):
    simulation = make_simulation(month, {'salary': 20000})
    expected_result = 0.02 * 6000 + 0.06 * 6400 + 0.12 * 7600
    tools.assert_near(simulation.calculate('social_security_contribution', month), [expected_result], absolute_error_margin = 0.01)


def test_non_existing_variable(make_simulation, month):
    simulation = make_simulation(month, {})

    with pytest.raises(VariableNotFoundError):
        simulation.calculate('non_existent_variable', 2013)


def test_calculate_variable_with_wrong_definition_period(make_simulation, year):
    simulation = make_simulation(year, {})

    with pytest.raises(ValueError) as error:
        simulation.calculate('basic_income', year)

    error_message = str(error.value)
    expected_words = ['period', f'{year}', 'month', 'basic_income', 'ADD']

    for word in expected_words:
        assert word in error_message, 'Expected "{}" in error message "{}"'.format(word, error_message)


def test_divide_option_on_month_defined_variable(make_simulation, month):
    simulation = make_simulation(month, {})

    with pytest.raises(ValueError):
        simulation.person('disposable_income', month, options = [populations.DIVIDE])


def test_divide_option_with_complex_period(make_simulation, month):
    simulation = make_simulation(month, {})
    quarter = periods.period('2013-12').last_3_months

    with pytest.raises(ValueError):
        simulation.household('housing_tax', quarter, options = [populations.DIVIDE])


def test_input_with_wrong_period(make_simulation, month):

    with pytest.raises(ValueError):
        make_simulation(month, {'basic_income': {2015: 12000}})


def test_variable_with_reference(
        make_isolated_simulation,
        isolated_tax_benefit_system,
        month,
        ):
    simulation_base = make_isolated_simulation(
        isolated_tax_benefit_system,
        month,
        {"salary": 4000},
        )

    revenu_disponible_avant_reforme = simulation_base.calculate(
        "disposable_income",
        month,
        )

    assert(revenu_disponible_avant_reforme > 0)

    class disposable_income(Variable):
        definition_period = periods.MONTH

        def formula(household, month):
            return household.empty_array()

    isolated_tax_benefit_system.update_variable(disposable_income)

    simulation_reform = make_isolated_simulation(
        isolated_tax_benefit_system,
        month,
        {"salary": 4000},
        )

    revenu_disponible_apres_reforme = simulation_reform.calculate(
        "disposable_income",
        month,
        )

    assert(revenu_disponible_apres_reforme == 0)


def test_variable_name_conflict(tax_benefit_system):

    class disposable_income(Variable):

        reference = 'disposable_income'
        definition_period = periods.MONTH

        def formula(household, month):
            return household.empty_array()

    with pytest.raises(VariableNameConflictError):
        tax_benefit_system.add_variable(disposable_income)
