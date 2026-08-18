from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from secure_aggregation import ModelUpdate, SecureAggregationProtocol

def run():
    protocol=SecureAggregationProtocol('dropout-1','v1',2)
    for org in ('Organization A','Organization B','Organization C','Organization D'): protocol.register_participant(org)
    protocol.setup_masks()
    for org,data in [('Organization A',[2,3]),('Organization B',[4,5]),('Organization D',[1,2])]: protocol.submit(ModelUpdate(org,'dropout-1','v1',data))
    result=protocol.complete(); print('Recovered aggregate:',result.aggregate_update.tolist()); print('Missing:',sorted(result.dropout_information.missing))
if __name__=='__main__': run()
