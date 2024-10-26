import pandas as pd
from scipy.io import loadmat

from src.toolbox.path_directories import DIR_MEAN

def get_mean_file(id_mach):
    """

    Parameters
    ----------
    id_mach
        the index of the Mach number referenced in the Mach.dat

    Returns
    -------


    """

    mean_files = DIR_MEAN.glob('*.mat').name



    # Sort files by extracting the numeric part of the filename
    sorted_mean_files = sorted(mean_files, key=lambda file: int(file.stem.split('_')[-1]))

    # Return a dictionary with {i: mean_i.mat} structure
    return sorted_mean_files[id_mach - 1].name

names = ['x', 'r', 'rho', 'ux', 'ur', 'u_theta', 'T', 'P']
mean_file = loadmat(DIR_MEAN / 'mean_1.mat')
data = mean_file['arr']
Nx, Nr, Nvalues = data.shape

data_dict = {name: pd.DataFrame(data[:, :, i], index=range(Nx), columns=range(Nr)) for i, name in enumerate(names)}





