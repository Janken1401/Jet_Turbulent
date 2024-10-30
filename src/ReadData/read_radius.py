import numpy as np

from toolbox.path_directories import DIR_DATA

rans_69pt_file = DIR_DATA / 'RANS69pt.dat'

def get_r_grid():
    """

    Returns
    -------
    ndarray: containing the 69 points along r from the RANS69pt.dat
    """
    return np.loadtxt(rans_69pt_file)
