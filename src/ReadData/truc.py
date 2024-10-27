import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.io import loadmat

from toolbox.path_directories import DIR_MEAN
plt.style.use('ggplot')
# Define ranges for x and r
names = ['x', 'r', 'rho', 'ux', 'ur', 'u_theta', 'T', 'P']
mean_file = loadmat(DIR_MEAN / 'mean_1.mat')
data = mean_file['arr']

Nx, Nr, Nvalues = data.shape

data_dict = {name: pd.DataFrame(data[:, :, i], index=range(Nx), columns=range(Nr)) for i, name in enumerate(names)}

x = data_dict["x"]
r = data_dict["r"]
P = data_dict["P"]
ux = data_dict["ux"]
ur = data_dict["ur"]
u_theta = data_dict["u_theta"]
T = data_dict["T"]
rho = data_dict["rho"]

def select_value_in_field(value, x_max=10, r_max=3):
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
    x_mask = (x.iloc[:, 0] >= 0) & (x.iloc[:, 0] <= x_max)
    r_mask = (r.iloc[0, :] >= 0) & (r.iloc[0, :] <= r_max)

    # Apply the masks to select the subarray
    x_sub = x.loc[x_mask, r_mask].values
    r_sub = r.loc[x_mask, r_mask].values
    value_sub = value.loc[x_mask, r_mask].values
    return x_sub, r_sub, value_sub


def plot_value_in_field(value, x_max=10, r_max=3):
    from toolbox.fig_parameters import RANS_FIGSIZE
    x, r, value = select_value_in_field(value, x_max, r_max)
    plt.figure(figsize=RANS_FIGSIZE, layout='constrained')
    plt.contourf(x, r, value, levels=100, cmap='coolwarm')
    plt.colorbar()
    plt.show()

plot_value_in_field(P, x_max=10, r_max=3)