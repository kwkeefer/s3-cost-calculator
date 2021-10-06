from s3calc import s3_costs


def test_header_calculate_costs_for_all_storage_types(tmpdir, pricing_data):
    s3_costs.calculate_costs_for_all_storage_types(
        pricing_data=pricing_data,
        number_of_objects=10000000000,
        total_gb=10000,
        outfile=f"{tmpdir}/s3_storage_calculations__10000gb_10000000000objects.csv"
    )

    with open(f"{tmpdir}/s3_storage_calculations__10000gb_10000000000objects.csv") as f:
        header = f.read().splitlines()[0]
        assert header == "storage_type,monthly_cost,transition_cost,monthly_savings,months_to_break_even,savings_after_1_yr,savings_after_3_yrs,cost_to_retrieve_10_percent"


def test_deep_glacier_calculate_costs_for_all_storage_types(tmpdir, pricing_data):
    s3_costs.calculate_costs_for_all_storage_types(
        pricing_data=pricing_data,
        number_of_objects=10000000000,
        total_gb=10000,
        outfile=f"{tmpdir}/s3_storage_calculations__10000gb_10000000000objects.csv"
    )

    with open(f"{tmpdir}/s3_storage_calculations__10000gb_10000000000objects.csv") as f:
        deep_glacier = f.read().splitlines()[4]
        assert deep_glacier == 'DEEP_GLACIER,"1,914.20","500,000,000.00","-1,704.20",None,None,None,"25,400,002.51"'

