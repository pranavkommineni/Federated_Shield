import pytest
from secure_aggregation import SecureAggregationProtocol
def test_server_has_no_mask_manager_or_plaintext_masking_method():
    server=SecureAggregationProtocol('r','v',2)
    assert not hasattr(server.aggregator,'mask_manager')
    assert not hasattr(server.aggregator,'protect')
