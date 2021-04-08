import pytest

from openfisca_country_template import CountryTaxBenefitSystem


@pytest.fixture(scope = "module")
def tax_benefit_system():
    return CountryTaxBenefitSystem()
