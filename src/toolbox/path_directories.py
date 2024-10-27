from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # Points to the Jet_Turbulent directory
DIR_DATA = BASE_DIR / 'Data'
DIR_MEAN = DIR_DATA / 'MeanFlow'
DIR_STABILITY = DIR_DATA / 'Stability'
DIR_OUT = BASE_DIR / 'Output'

CASE_NUMBER = 10
RANS_FILES = {i: f'mean_{i}.mat' for i in range(1,CASE_NUMBER+1)}
