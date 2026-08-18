from time import perf_counter
from secure_aggregation import ModelUpdate, SecureAggregationProtocol
def benchmark(count):
    start=perf_counter(); p=SecureAggregationProtocol('bench','v1',2)
    for index in range(count): p.register_participant(f'org-{index}')
    p.setup_masks(); setup=perf_counter()
    for index in range(count): p.submit(ModelUpdate(f'org-{index}','bench','v1',[float(index)]*100))
    masked=perf_counter(); p.complete(); end=perf_counter()
    return {'participants':count,'setup_seconds':setup-start,'masking_seconds':masked-setup,'aggregation_seconds':end-masked,'total_seconds':end-start}
if __name__=='__main__':
    for count in (3,5,10): print(benchmark(count))
