from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from secure_aggregation.examples.basic_demo import run
run()
