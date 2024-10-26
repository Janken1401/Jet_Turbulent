import pandas as pd
from os.path import join as pjoin

from src.toolbox.constantes import __DIR_DATA__

path_info = pjoin(__DIR_DATA__, 'info.dat')
path_mach = pjoin(__DIR_DATA__, 'Mach.dat')

def get_reference_values():
    return pd.read_csv(path_info, delimiter=r'\s+', comment='#', names=["ux", "rho", "T", "P"])


def get_mach_reference():

    columns = ['Id', 'Ma']
    mach_df = pd.read_csv(path_mach, delimiter=r'\s+', comment='#', header=None, names=columns)

    return mach_df

mach = get_mach_reference()

ref_quantities = get_reference_values()


def get_reference_ux():
    return get_reference_values()['ux']


def get_reference_rho():
    return get_reference_values()['rho']


def get_reference_T():
    return get_reference_values()['T']


def get_reference_P():
    return get_reference_values()['P']
