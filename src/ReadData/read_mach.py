import pandas as pd

from src.toolbox.path_directories import DIR_DATA

path_mach = DIR_DATA / 'Mach.dat'


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
    mach_df = pd.read_csv(path_mach, delimiter=r'\s+', header=None, names=['ID', 'Ma'])

    return mach_df
