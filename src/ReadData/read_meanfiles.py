import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt

from src.toolbox.path_directories import DIR_MEAN, RANS_FILES


def get_RANS_values(ID_MACH):
    """
    Retrieve values of the RANS mean field based on the mach case selected
    Parameters
    ----------
    ID_MACH
        int: the mach case selected. Here ID_MACH = {1, 10}
    Returns
    -------
    Dict: contains DataFrame for all the values e.g:
        P = get_RANS_values(ID_MACH)['P'] retrieve the pressure field
    """
    names = ['x', 'r', 'rho', 'ux', 'ur', 'u_theta', 'T', 'P']
    mean_file = loadmat(DIR_MEAN / RANS_FILES[ID_MACH])
    data = mean_file['arr']
    Nx, Nr, Nvalues = data.shape

    return {name: pd.DataFrame(data[:, :, i], index=range(Nx), columns=range(Nr)) for i, name in enumerate(names)}


def select_value_in_field(value, ID_MACH=1, x_max=10, r_max=3):
    """
    Return the value in the wanted domain

    Parameters
    ----------
    value: DataFrame
        values to retrieve in the wanted domain.
        Value available : ux, ur, u_theta, T, P, Ma
    x_max: DataFrame
        maximum value on the x direction
    r_max: DataFrame
        maximum value o the radial direction

    Returns
    -------
    x_sub: DataFrame
        the x values in the wanted domain
    r_sub: DataFrame
        the r values in the wanted domain
    value_sub: DataFrame
        the values in the wanted domain
    """
    x = get_RANS_values(ID_MACH)['x']
    r = get_RANS_values(ID_MACH)['r']
    value = get_RANS_values(ID_MACH)[value]
    x_mask = (x.iloc[:, 0] >= 0) & (x.iloc[:, 0] <= x_max)
    r_mask = (r.iloc[0, :] >= 0) & (r.iloc[0, :] <= r_max)

    # Apply the masks to select the subarray
    x_sub = x.loc[x_mask, r_mask].values
    r_sub = r.loc[x_mask, r_mask].values
    value_sub = value.loc[x_mask, r_mask].values
    return x_sub, r_sub, value_sub

def plot_value_in_field(x, r, value):
    from toolbox.fig_parameters import RANS_FIGSIZE
    plt.style.use('ggplot')
    plt.figure(figsize=RANS_FIGSIZE, layout='constrained')
    plt.contourf(x, r, value, levels=100, cmap='coolwarm')
    plt.colorbar()
    plt.show()

x, r, ux = select_value_in_field('ux', 1)
plot_value_in_field(x, r, ux)








