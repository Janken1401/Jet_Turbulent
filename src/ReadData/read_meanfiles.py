import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt

from src.toolbox.path_directories import DIR_MEAN, RANS_FILES
from toolbox.fig_parameters import RANS_FIGSIZE
from src.ReadData.read_info import get_mach_reference

rans_value_names = ['x', 'r', 'rho', 'ux', 'ur', 'ut', 'T', 'p']


class ransField:
    def __init__(self, ID_MACH):
        """

        Parameters
        ----------
        ID_MACH
        """
        self.ID_MACH = ID_MACH
        rans_file = DIR_MEAN / RANS_FILES[self.ID_MACH]

        self.mach = get_mach_reference().loc[self.ID_MACH - 1]
        self.rans_field_array = loadmat(rans_file)['arr']
        self.Nx, self.Nr, self.Nvalues = self.rans_field_array.shape
        self.rans_field = self.get_rans_values()
        self.x = self.rans_field['x']
        self.r = self.rans_field['r']
        self.rho = self.rans_field['rho']
        self.ux = self.rans_field['ux']
        self.ur = self.rans_field['ur']
        self.ut = self.rans_field['ut']
        self.T = self.rans_field['T']
        self.p = self.rans_field['p']

    def get_rans_values(self):
        """
        Retrieve values of the RANS mean field based on the mach case selected

        Returns
        -------
        Dict: a dict containing DataFrame for each value computed in the RANS field
        """
        return {name: pd.DataFrame(self.rans_field_array[:, :, i], index=range(self.Nx), columns=range(self.Nr))
                for i, name in enumerate(rans_value_names)}

    def get_value_in_field(self, value, x_max=10, r_max=3):
        """
        Return the value in the wanted domain

        Parameters
        ----------
        value: DataFrame
            values to retrieve in the wanted domain.
            Value available : x, r, rho, ux, ur, ut, T, p, Ma
        x_max: int - optional
            maximum value on the x direction
        r_max: int - optional
            maximum value on the radial direction

        Returns
        -------
        x_sub: DataFrame
            the x values in the wanted domain
        r_sub: DataFrame
            the r values in the wanted domain
        value_sub: DataFrame
            the values in the wanted domain
        """
        x_mask = (self.x.iloc[:, 0] >= 0) & (self.x.iloc[:, 0] <= x_max)
        r_mask = (self.r.iloc[0, :] >= 0) & (self.r.iloc[0, :] <= r_max)

        # Apply the masks to select the subarray
        x_sub = self.x.loc[x_mask, r_mask].values
        r_sub = self.r.loc[x_mask, r_mask].values
        value_sub = value.loc[x_mask, r_mask].values
        return x_sub, r_sub, value_sub

    def plot_x(self, x_max=10, r_max=3):
        self.plot_value_in_field(self.x, x_max, r_max)

    def plot_r(self, x_max=10, r_max=3):
        self.plot_value_in_field(self.r, x_max, r_max)

    def plot_rho(self, x_max=10, r_max=3):
        self.plot_value_in_field(self.rho, x_max, r_max)

    def plot_ux(self, x_max=10, r_max=3):
        self.plot_value_in_field(self.ux, x_max, r_max)

    def plot_ur(self, x_max=10, r_max=3):
        self.plot_value_in_field(self.ur, x_max, r_max)

    def plot_ut(self, x_max=10, r_max=3):
        self.plot_value_in_field(self.ut, x_max, r_max)

    def plot_T(self, x_max=10, r_max=3):
        self.plot_value_in_field(self.T, x_max, r_max)

    def plot_p(self, x_max=10, r_max=3):
        self.plot_value_in_field(self.p, x_max, r_max)

    def plot_value_in_field(self, value, x_max=10, r_max=3):
        x, r, value = self.get_value_in_field(value, x_max, r_max)
        plt.style.use('ggplot')
        plt.figure(figsize=RANS_FIGSIZE, layout='constrained')
        plt.contourf(x, r, value, levels=100, cmap='coolwarm')
        plt.xlabel('x/D')
        plt.ylabel('r/D')
        plt.title(r'\hat{{self.value}}'.format(value))
        plt.colorbar()
        plt.show()

rans_1 = ransField(1)

rans_1.plot_p()