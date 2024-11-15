import pandas as pd

from src.toolbox.path_directories import DIR_DATA

path_mach = DIR_DATA / 'Mach.dat'


def get_mach_reference(ID):
    """Retrieve all the Mach numbers

    Returns
    -------
    DataFrame
        a DataFrame containing a specific Mach numbers used. Each values of Mach numbers are associated
        with an ID such as :
            ID       Ma
            1  0.97335

    """
    mach_df = pd.read_csv(path_mach, delimiter=r'\s+', header=None, names=['ID', 'Ma'])
    mach_df.set_index('ID', inplace=True)

    return mach_df.loc[ID]
