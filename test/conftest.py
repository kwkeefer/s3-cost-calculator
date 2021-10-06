import pytest


@pytest.fixture()
def pricing_data():
    return {
        "frequent": {
            "storage_per_gb": 0.021,
            "1000_get_requests": 0.0004,
            "1000_lifecycle_transition_into": 0,
            "1000_data_retrieval_requests": 0,
            "data_retrievals_per_gb": 0
        },
        "infrequent": {
            "storage_per_gb": 0.0125,
            "1000_get_requests": 0.001,
            "1000_lifecycle_transition_into": 0.01,
            "1000_data_retrieval_requests": 0,
            "data_retrievals_per_gb": 0.01
        },
        "glacier": {
            "storage_per_gb": 0.004,
            "1000_get_requests": 0.0004,
            "1000_lifecycle_transition_into": 0.03,
            "1000_data_retrieval_requests": 0.025,
            "data_retrievals_per_gb": 0.0025
        },
        "deep_glacier": {
            "storage_per_gb": 0.00099,
            "1000_get_requests": 0.0004,
            "1000_lifecycle_transition_into": 0.05,
            "1000_data_retrieval_requests": 0.025,
            "data_retrievals_per_gb": 0.0025
        }
    }
