import numpy as np
import pandas as pd

from src.ReadData.read_mach import get_mach_reference
from src.toolbox.path_directories import DIR_DATA
from src.toolbox.dimless_reference_values import gamma, R

path_info = DIR_DATA / 'info.dat'


def get_reference_values():
    """Retrieve Reference Values for every RANS fields

    Returns
    -------
    DataFrame
        a DataFrame containing all values for all the Mach numbers like :
            ux       rho           T              P
        0   311.529138  1.576135  254.860326  115326.441784
        1   311.916903  1.574279  254.740191  115136.336935
        2   313.535065  1.566509  254.236346  114341.477460
        3   314.254834  1.563060  254.011995  113989.019331
        4   314.776053  1.560574  253.850328  113735.289238

    """

    # Used read_csv instead with space delimiter instead of read_fwf in case
    # of floating inconsistency.
    return pd.read_csv(path_info,
                       delimiter=r'\s+',
                       skiprows=1,
                       names=["ux", "rho", "T", "P"])


def compare_mach():
    """
    Compare the reference Mach number with the Mach number computed
    with the reference values for the RANS cases
    Returns
    -------
    DataFrame
        a DataFrame with the relative error for each Mach number

    """

    ref_values = get_reference_values()
    ref_values['Ma'] = ref_values['ux'] / np.sqrt(gamma * R * ref_values['T'])
    Mach_ref = get_mach_reference()
    error = 100 * np.abs(ref_values['Ma'] - Mach_ref['Ma']) / Mach_ref['Ma']

    return error


error = compare_mach()
