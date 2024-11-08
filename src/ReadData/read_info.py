import pandas as pd

from src.toolbox.path_directories import DIR_DATA

path_info = DIR_DATA / 'info.dat'


def get_reference_values():
    """Retrieve Reference Values for every RANS fields

    Returns
    -------
    DataFrame
        a DataFrame containing all values for all the Mach numbers like :
            ux          rho       T            P
        0   311.529138  1.576135  254.860326  115326.441784
        1   311.916903  1.574279  254.740191  115136.336935
        2   313.535065  1.566509  254.236346  114341.477460
        3   314.254834  1.563060  254.011995  113989.019331
        4   314.776053  1.560574  253.850328  113735.289238

    """

    # Used read_csv instead with space delimiter instead of read_fwf in case
    # of floating inconsistency.
    with open(path_info, "r") as file:
        header = file.readline().strip("# ").split()

    df = pd.read_csv(path_info,
                       delimiter=r'\s+',
                       comment='#', names=header, skiprows=1)
    df.index = df.index + 1
    return df
