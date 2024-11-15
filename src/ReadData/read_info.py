import pandas as pd

from src.toolbox.path_directories import DIR_DATA

path_info = DIR_DATA / 'info.dat'


def get_reference_values(ID_MACH):
    """Retrieve Reference Values for every RANS fields

    Returns
    -------
    DataFrame
        a DataFrame containing all values for a specific Mach numbers like :
            ux          rho       T            P
        1   311.529138  1.576135  254.860326  115326.441784


    """

    # Used read_csv instead with space delimiter instead of read_fwf in case
    # of floating inconsistency.
    with open(path_info, "r") as file:
        header = file.readline().strip("# ").split()

    df = pd.read_csv(path_info,
                       delimiter=r'\s+',
                       comment='#', names=header, skiprows=1)
    df.index = df.index + 1
    return df.loc[ID_MACH]
