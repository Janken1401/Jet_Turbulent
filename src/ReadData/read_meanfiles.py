import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt
plt.style.use('ggplot')
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
x = data_dict['x']
x = x

r = data_dict['r']
rho = data_dict['rho']
ux = data_dict['ux']
ur = data_dict['ur']
u_theta = data_dict['u_theta']
T = data_dict['T']
P = data_dict['P']

plt.contourf(x <= 10,r <= 3, P)
plt.show()








