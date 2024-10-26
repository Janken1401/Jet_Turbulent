import pandas as pd
from src.toolbox.constantes import DIR_DATA

path_info = DIR_DATA / 'info.dat'
path_mach = DIR_DATA / 'Mach.dat'


def get_reference_values():
    return pd.read_csv(path_info,
                       delimiter=r'\s+',
                       skiprows=1,
                       names=["ux", "rho", "T", "P"])


def get_mach_reference():
    columns = ['Id', 'Ma']
    mach_df = pd.read_csv(path_mach, delimiter=r'\s+', header=None, names=columns)

    return mach_df


mach = get_mach_reference()
print(mach)
ref_quantities = get_reference_values()


def get_reference_ux():
    return get_reference_values()['ux']


def get_reference_rho():
    return get_reference_values()['rho']


def get_reference_T():
    return get_reference_values()['T']


def get_reference_P():
    return get_reference_values()['P']
