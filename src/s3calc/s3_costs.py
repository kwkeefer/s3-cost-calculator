import argparse
import os
from typing import Union

from .utils import _read_config_file, format_float


def _calculate_s3_standard_or_ia_storage_cost(pricing_data: dict, s3_storage_type: str,
                                              total_gb_stored: Union[int, float]):
    """ Calculate monthly storage cost for S3 frequent or infrequent access """
    if s3_storage_type not in ['frequent', 'infrequent']:
        raise ValueError

    return total_gb_stored * pricing_data[s3_storage_type]['storage_per_gb']


def _calculate_glacier_or_deep_glacier_storage_cost(pricing_data: dict, s3_storage_type: str,
                                                    number_of_objects: Union[int, float],
                                                    total_gb_stored: Union[int, float]) -> float:
    """
    Calculate monthly cost for S3 glacier or deep glacier.

    For each object that is stored in S3 Glacier or S3 Glacier Deep Archive,
    Amazon S3 adds 40 KB of chargeable overhead for metadata, with 8KB charged at
    S3 Standard rates and 32 KB charged at S3 Glacier or S3 Deep Archive rates.

    https://www.calculatorsoup.com/calculators/conversions/computerstorage.php
    """
    if s3_storage_type not in ['glacier', 'deep_glacier']:
        raise ValueError

    metadata_cost_1 = number_of_objects * pricing_data[s3_storage_type]['storage_per_gb'] * (
            32 / 2 ** 20)  # KiB to GiB conversion
    metadata_cost_2 = number_of_objects * pricing_data['frequent']['storage_per_gb'] * (
            8 / 2 ** 20)  # KiB to GiB conversion
    storage_cost = total_gb_stored * pricing_data[s3_storage_type]['storage_per_gb']
    return metadata_cost_1 + metadata_cost_2 + storage_cost


def calculate_storage_costs(pricing_data: dict, s3_storage_type: str, total_gb_stored: Union[int, float],
                            number_of_objects: Union[int, float] = None) -> float:
    """ Calculate storage costs for all storage types

    Args:
        pricing_data: dictionary containing pricing data for all storage types
        s3_storage_type: which s3 storage type to check costs for
        total_gb_stored: how many total gbs are being stored
        number_of_objects: how many objects are being stored

    Returns: (float) price

    """
    if s3_storage_type not in ['frequent', 'infrequent', 'glacier', 'deep_glacier']:
        raise ValueError

    if s3_storage_type in ['frequent', 'infrequent']:
        return _calculate_s3_standard_or_ia_storage_cost(pricing_data, s3_storage_type, total_gb_stored)
    else:
        return _calculate_glacier_or_deep_glacier_storage_cost(pricing_data, s3_storage_type, number_of_objects,
                                                               total_gb_stored)


def _calculate_standard_or_ia_retrieval_costs(pricing_data: dict, s3_storage_type: str,
                                              number_of_objects: Union[int, float],
                                              total_gb_retrieved: Union[int, float]) -> float:
    per_obj_costs = pricing_data[s3_storage_type]['1000_get_requests'] * number_of_objects
    per_gb_costs = pricing_data[s3_storage_type]['data_retrievals_per_gb'] * total_gb_retrieved
    return per_gb_costs + per_obj_costs


def calculate_transition_costs(pricing_data: dict, s3_storage_type_to_transition_to: str,
                               number_of_objects: Union[int, float]):
    if s3_storage_type_to_transition_to not in ['frequent', 'infrequent', 'glacier', 'deep_glacier']:
        raise ValueError

    return number_of_objects * pricing_data[s3_storage_type_to_transition_to]['1000_lifecycle_transition_into']


def calculate_retrieval_costs(pricing_data: dict, s3_storage_type: str, number_of_objects: Union[int, float],
                              total_gb_retrieved: Union[int, float],
                              temporary_restore_duration: int = None) -> float:
    """
    Amazon S3 objects that are stored in the S3 Glacier or S3 Glacier Deep Archive storage classes 
    are not immediately accessible. To access an object in these storage classes, you must restore a 
    temporary copy of it to its S3 bucket for a specified duration (number of days). 
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects.html
    """
    if s3_storage_type not in ['frequent', 'infrequent', 'glacier', 'deep_glacier']:
        raise ValueError
    if temporary_restore_duration is None:
        raise ValueError

    per_obj_costs = pricing_data[s3_storage_type]['1000_data_retrieval_requests'] * number_of_objects
    per_gb_costs = pricing_data[s3_storage_type]['data_retrievals_per_gb'] * total_gb_retrieved
    temp_storage_costs = pricing_data['frequent']['storage_per_gb'] * (temporary_restore_duration / 30)
    read_costs = pricing_data['frequent']['1000_get_requests'] * number_of_objects
    return per_gb_costs + per_obj_costs + temp_storage_costs + read_costs


def calculate_costs(pricing_data: dict, s3_storage_type_to_transition_to: str, number_of_objects: Union[int, float],
                    total_gb: Union[int, float]) -> dict:
    """ Calculate amount of time (in months) required to break even when transitioning
     from frequent access to another storage type. """

    if s3_storage_type_to_transition_to not in ['infrequent', 'glacier', 'deep_glacier']:
        raise ValueError

    transition_costs = calculate_transition_costs(pricing_data, s3_storage_type_to_transition_to, number_of_objects)
    current_monthly_costs = calculate_storage_costs(pricing_data, 'frequent', total_gb)

    monthly_costs_after_transition = calculate_storage_costs(pricing_data, s3_storage_type_to_transition_to, total_gb,
                                                             number_of_objects)

    ten_percent_data_retrieval = calculate_retrieval_costs(
        pricing_data=pricing_data,
        s3_storage_type=s3_storage_type_to_transition_to,
        number_of_objects=(number_of_objects / 10),
        total_gb_retrieved=(total_gb / 10),
        temporary_restore_duration=14
    )

    costs = {
        'transition_costs': transition_costs,
        'current_monthly_costs': current_monthly_costs,
        'monthly_costs_after_transition': monthly_costs_after_transition,
        '10_percent_data_retrieval_costs': ten_percent_data_retrieval,
        'monthly_savings': current_monthly_costs - monthly_costs_after_transition
    }

    # if transition costs are greater than savings after three years, it is not worth the transition
    if (current_monthly_costs < monthly_costs_after_transition) or (
            transition_costs / 36 > costs['monthly_savings'] * 36):
        costs['break_even_time'] = None
        costs['savings_after_12_months'] = None
        costs['savings_after_36_months'] = None
    else:
        costs['break_even_time'] = transition_costs / costs['monthly_savings']
        costs['savings_after_12_months'] = (costs['monthly_savings'] * 12) - transition_costs
        costs['savings_after_36_months'] = (costs['monthly_savings'] * 36) - transition_costs
    return costs


def calculate_costs_for_all_storage_types(pricing_data: dict, number_of_objects: Union[int, float],
                                          total_gb: Union[int, float], outfile: str):
    if outfile is None:
        outfile = f"s3_storage_calculations__{total_gb}gb_{number_of_objects}objects.csv"

    f = open(outfile, "w")
    f.write(
        "storage_type,monthly_cost,transition_cost,monthly_savings,months_to_break_even,savings_after_1_yr,savings_after_3_yrs,cost_to_retrieve_10_percent\n")

    frequent_storage_costs = calculate_storage_costs(
        pricing_data=pricing_data,
        s3_storage_type='frequent',
        total_gb_stored=total_gb,
        number_of_objects=number_of_objects
    )
    frequent_retrieval_costs_10_percent = calculate_retrieval_costs(
        pricing_data=pricing_data,
        s3_storage_type='frequent',
        number_of_objects=(number_of_objects / 10),
        total_gb_retrieved=(total_gb / 10),
        temporary_restore_duration=7
    )

    f.write(
        f"FREQUENT,{format_float(frequent_storage_costs)},0,0,0,0,0,{format_float(frequent_retrieval_costs_10_percent)}\n")

    for storage_type in ['infrequent', 'glacier', 'deep_glacier']:
        costs = calculate_costs(pricing_data, storage_type, number_of_objects, total_gb)

        f.write(
            f"{storage_type.upper()}," +
            f"{format_float(costs['monthly_costs_after_transition'])}," +
            f"{format_float(costs['transition_costs'])}," +
            f"{format_float(costs['monthly_savings'])}," +
            f"{format_float(costs['break_even_time'])}," +
            f"{format_float(costs['savings_after_12_months'])}," +
            f"{format_float(costs['savings_after_36_months'])}," +
            f"{format_float(costs['10_percent_data_retrieval_costs'])}\n")

    f.close()
    print(f"Results saved in {outfile}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", help="Region to look at in the pricing_info.yml file.", default="us-west-2")
    parser.add_argument("--config", help="Path to config file.", default=None)
    parser.add_argument("--gb", help="Total size of data in GiB", type=int)
    parser.add_argument("--number_of_objects", help="Number of objects to transition.", type=int)
    parser.add_argument("--outfile", help="Name / path to write output csv file.")
    args = parser.parse_args()

    if args.config is None:
        args.config = os.path.dirname(__file__) + "/pricing_info.yml"

    config = _read_config_file(args.config)

    calculate_costs_for_all_storage_types(config[args.region], args.number_of_objects, args.gb, args.outfile)
