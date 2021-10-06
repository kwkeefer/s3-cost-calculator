import pytest

from s3calc import s3_costs


def test_invalid_storage_type_calculate_s3_standard_or_ia_storage_cost(pricing_data):
    with pytest.raises(ValueError):
        s3_costs._calculate_s3_standard_or_ia_storage_cost(
            pricing_data=pricing_data,
            s3_storage_type="glacier",
            total_gb_stored=1
        )


def test_frequent_calculation_calculate_s3_standard_or_ia_storage_cost(pricing_data):
    calculation = s3_costs._calculate_s3_standard_or_ia_storage_cost(
        pricing_data=pricing_data,
        s3_storage_type="frequent",
        total_gb_stored=1
    )
    assert calculation == 0.021


def test_invalid_storage_type_calculate_glacier_or_deep_glacier_storage_cost(pricing_data):
    with pytest.raises(ValueError):
        s3_costs._calculate_glacier_or_deep_glacier_storage_cost(
            pricing_data=pricing_data,
            s3_storage_type="frequent",
            number_of_objects=1,
            total_gb_stored=1
        )


def test_glacier_calculation_calculate_glacier_or_deep_glacier_storage_cost(pricing_data):
    calculation = s3_costs._calculate_glacier_or_deep_glacier_storage_cost(
        pricing_data=pricing_data,
        s3_storage_type="glacier",
        number_of_objects=10000000000,
        total_gb_stored=10000
    )
    assert calculation == 2862.8759765625


def test_frequent_calculate_storage_costs(pricing_data):
    calculation = s3_costs.calculate_storage_costs(
        pricing_data=pricing_data,
        s3_storage_type="frequent",
        total_gb_stored=1,
        number_of_objects=1
    )
    assert calculation == 0.021


def test_glacier_calculate_storage_costs(pricing_data):
    calculation = s3_costs.calculate_storage_costs(
        pricing_data=pricing_data,
        s3_storage_type="glacier",
        number_of_objects=10000000000,
        total_gb_stored=10000
    )
    assert calculation == 2862.8759765625


def test_frequent_calculate_standard_or_ia_retrieval_costs(pricing_data):
    calculation = s3_costs._calculate_standard_or_ia_retrieval_costs(
        pricing_data=pricing_data,
        s3_storage_type="frequent",
        number_of_objects=10000000000,
        total_gb_retrieved=10000
    )
    assert calculation == 4000000


def test_infrequent_calculate_standard_or_ia_retrieval_costs(pricing_data):
    calculation = s3_costs._calculate_standard_or_ia_retrieval_costs(
        pricing_data=pricing_data,
        s3_storage_type="infrequent",
        number_of_objects=10000000000,
        total_gb_retrieved=10000
    )
    assert calculation == 10000100

def test_infrequent_calculate_costs(pricing_data):
    costs = s3_costs.calculate_costs(
        pricing_data=pricing_data,
        s3_storage_type_to_transition_to="infrequent",
        number_of_objects=10000000000,
        total_gb=1
    )
    assert costs['break_even_time'] is None
