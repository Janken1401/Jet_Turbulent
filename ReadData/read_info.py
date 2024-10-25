import pandas as pd
from toolbox.constantes import __DIR__
from toolbox.read_data import load_data

path_info = __DIR__ + "info.dat"

# ref_quantites = load_data(path_info)



def get_reference_quantites():
    return pd.read_csv(path_info, delimiter=r'\s+', comment='#',names=["ux", "rho",
                                                              "T", "P"])
def get_ux():
    pass
