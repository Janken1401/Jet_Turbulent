import pandas as pd
from src.toolbox.path_directories import DIR_DATA

path_info = DIR_DATA / 'info.dat'
path_mach = DIR_DATA / 'Mach.dat'


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


def get_mach_reference():
    """Retrieve all the Mach numbers

    Returns
    -------
    DataFrame
        a DataFrame containing all the Mach numbers used. Each values of Mach numbers are associated
        with an ID such as :
            ID       Ma
        0    1  0.97335
        1    2  0.97479
        2    3  0.98081
        3    4  0.98350
        4    5  0.98544
    """
    columns = ['ID', 'Ma']
    mach_df = pd.read_csv(path_mach, delimiter=r'\s+', header=None, names=columns)

    return mach_df

