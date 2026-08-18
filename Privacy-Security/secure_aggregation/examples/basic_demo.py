from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from secure_aggregation import ModelUpdate, SecureAggregationClient, SecureAggregationProtocol

def run():
    clients={org:SecureAggregationClient(org) for org in ('Organization A','Organization B','Organization C')}
    public={org:client.agreement_public_key for org,client in clients.items()}
    for client in clients.values(): client.configure_peers(public)
    protocol=SecureAggregationProtocol('demo-1','v1',2)
    for org,client in clients.items(): protocol.register_participant(org,client.verification_key)
    protocol.setup_masks()
    for org, data in [('Organization A',[2,3]),('Organization B',[4,5]),('Organization C',[1,2])]: protocol.submit_masked_update(clients[org].mask_update(ModelUpdate(org,'demo-1','v1',data)))
    result=protocol.complete()
    print('Server received protected updates only.')
    print('Secure aggregate:',result.aggregate_update.tolist())
    print('Plain aggregate: [7, 10]')
if __name__=='__main__': run()
