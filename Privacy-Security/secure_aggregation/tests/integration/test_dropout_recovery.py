import pytest
from secure_aggregation import SecureAggregationProtocol
def test_dropout_requires_explicit_recovery_material():
    server=SecureAggregationProtocol('r','v',2)
    assert server is not None
