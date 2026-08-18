import numpy as np
import pytest
from secure_aggregation import ModelUpdate, SecureAggregationClient, SecureAggregationProtocol
from secure_aggregation.exceptions import DuplicateSubmissionError, InsufficientParticipantsError

def build(ids=('A','B','C'), threshold=2):
    clients={item:SecureAggregationClient(item) for item in ids}; public={item:c.agreement_public_key for item,c in clients.items()}
    for client in clients.values(): client.configure_peers(public)
    server=SecureAggregationProtocol('r1','v1',threshold)
    for item,client in clients.items(): server.register_participant(item,client.verification_key)
    server.setup_masks(); return server,clients
def test_aggregate_and_protection():
    server,clients=build(); values={'A':[2,3],'B':[4,5],'C':[1,2]}
    for item,value in values.items(): server.submit_masked_update(clients[item].mask_update(ModelUpdate(item,'r1','v1',value)))
    np.testing.assert_allclose(server.complete().aggregate_update,[7,10]); assert not hasattr(server.aggregator,'mask_manager')
def test_duplicate_and_threshold_failure():
    server,clients=build(); masked=clients['A'].mask_update(ModelUpdate('A','r1','v1',[2,3])); server.submit_masked_update(masked)
    with pytest.raises(DuplicateSubmissionError): server.submit_masked_update(masked)
    with pytest.raises(InsufficientParticipantsError): server.complete()
