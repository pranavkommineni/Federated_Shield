from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from secure_aggregation.tests.performance.benchmark_aggregation import benchmark
for count in (3,5,10): print(benchmark(count))
