import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.io import loadmat
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from ReadData.read_info import get_reference_values
from src.toolbox.path_directories import DIR_MEAN, RANS_FILES
from toolbox.fig_parameters import RANS_FIGSIZE
from src.ReadData.read_mach import get_mach_reference
from src.ReadData.read_radius import get_r_grid
from src.toolbox.dimless_reference_values import gamma, rho_0, c_0, T_0, p_0

from src.ReadData.read_stability_field import perturbationField

rans_value_names = ['x', 'r', 'rho', 'ux', 'ur', 'ut', 'T', 'P']
r_grid = get_r_grid()

class ransField:
    def __init__(self, ID_MACH, St=0.4):
        """
        Parameters
        ----------
        ID_MACH : int
            ID of the Mach reference
        St : int or float
            Strouhal number
        """
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')

        self.ID_MACH = ID_MACH
        self.St = St
        self.mach = get_mach_reference().loc[self.ID_MACH - 1]
        self.rans_values = self._get_rans_values()
        self.rans_x = self.rans_values['x']
        self.rans_r = self.rans_values['r']

        pert_field = perturbationField(self.St, self.ID_MACH)
        self.pse_x = pert_field.pert_values['x']

    def interpolate_grid(self):
        rans_pse_values = self.convert_to_pse_reference()
        rans_pse_interpolated = {}

        for var_name in ('ux','ur','ut','P', 'rho'):
                interpolated_grid = np.zeros((len(self.pse_x), self.Nr))

                for i, r_point in enumerate(r_grid):
                    rans_values_at_x= rans_pse_values[var_name].iloc[:, i]

                    spline = CubicSpline(self.rans_x[i], rans_values_at_x)

                    interpolated_grid[:, i] = spline(self.pse_x)

                rans_pse_interpolated[var_name] = pd.DataFrame(interpolated_grid,
                                                               index=self.pse_x, columns=self.rans_r.columns)

        return rans_pse_interpolated



    def convert_to_pse_reference(self):
        """
        Set the dimensionized RANS into the PSE reference system

        Returns
        -------
        rans_pse: dict
            contains DataFrame of the rans field in PSE reference system
        """
        ref_values = get_reference_values().iloc[self.ID_MACH - 1]
        u_ref = ref_values['ux']
        rans_dim = self.rans_dimensionalization()
        rans_pse = {}
        rans_pse['ux'] = rans_dim['ux'] / u_ref
        rans_pse['ur'] = rans_dim['ur'] / u_ref
        rans_pse['ut'] = rans_dim['ut'] / u_ref
        rans_pse['T'] = rans_dim['T'] / ref_values['T']
        rans_pse['P'] = rans_dim['P'] / ref_values['P']
        rans_pse['rho'] = rans_dim['rho'] / ref_values['rho']

        return rans_pse

    def rans_dimensionalization(self):
        """
        Re-dimensionalize the RANS field before set it to the PSE reference

        Returns
        -------
        rans_dim : dict
            contains DataFrame of the rans field except for x and r
        """

        rans_dim = {}
        rans_dim['ux'] = self.rans_values['ux'] * c_0
        rans_dim['ur'] = self.rans_values['ur'] * c_0
        rans_dim['ut'] = self.rans_values['ut'] * c_0
        rans_dim['T'] = self.rans_values['T'] * T_0
        rans_dim['P'] = self.rans_values['P'] * p_0
        rans_dim['rho'] = self.rans_values['rho'] * rho_0

        return rans_dim

    def plot_mean_value(self, value, x_max=10, r_max=3):
        if value not in self.rans_values.keys():
            raise ValueError('value must be either x, r, rho, ux, ur, ut, T or P')
        if not isinstance(x_max, (int, float)) or not isinstance(r_max, (int, float)):
            raise TypeError('x_max and r_max must be an int or a float')

        titles = {'x': r'$\hat{x}$', 'r': r'$\hat{r}$', 'rho': r'$\hat{\rho}$',
                  'ux': r'$\hat{u_x}$', 'ur': r'$\hat{u_\theta}$', 'ut': r'$\hat{u_\theta}$',
                  'T': r'$\hat{T}$', 'P': r'$\hat{p}$'}

        self.plot(value, titles[value], x_max, r_max)

    def plot(self, value, title='', x_max=10, r_max=3):
        """

        Parameters
        ----------
        value: str
            value to plot. Avaible : 'ux', 'ur', 'ut', 'T', 'P'
        title
        x_max: int or float - optional
        r_max: int or float - optional
            provide the limit of the domain to plot the values

        Returns
        -------
        None
        """
        x, r, value = self.get_value_in_field(value, x_max, r_max)
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=RANS_FIGSIZE, layout='constrained')
        cs = ax.contourf(x, r, value, levels=100, cmap='coolwarm')
        plt.xlabel('x/D')
        plt.ylabel('r/D')
        tick_spacing = 1
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax.set_title(title)
        cbar = fig.colorbar(cs)
        tick_locator = ticker.MaxNLocator(nbins=5)
        cbar.locator = tick_locator
        cbar.set_ticks(ticks=tick_locator, vmin=value.min(), vmax=value.max())
        cbar.update_ticks()
        plt.show()

    def get_value_in_field(self, value, x_max=10, r_max=3):
        """
        Return the value in the wanted domain

        Parameters
        ----------
        value: 'str''
            values to retrieve in the wanted domain.
            Value available : x, r, rho, ux, ur, ut, T, p
        x_max: int - optional
            maximum value on the x direction
        r_max: int - optional
            maximum value on the radial direction

        Returns
        -------
        x_sub: Dataframe
            the x values in the wanted domain
        r_sub: DataFrame
            the r values in the wanted domain
        value_sub: DataFrame
            the values in the wanted domain
        """
        x_mask = (self.rans_x.iloc[:, 0] >= 0) & (self.rans_x.iloc[:, 0] <= x_max)
        r_mask = (self.rans_r.iloc[0, :] >= 0) & (self.rans_r.iloc[0, :] <= r_max)
        value = self.rans_values[value]
        # Apply the masks to select the subarray
        x_sub = self.rans_x.loc[x_mask, r_mask]
        r_sub = self.rans_r.loc[x_mask, r_mask]
        value_sub = value.loc[x_mask, r_mask]
        return x_sub, r_sub, value_sub


    def _get_rans_values(self):
        """
        Retrieve values of the RANS mean field based on the mach case selected

        Returns
        -------
        Dict: a dict containing DataFrame for each value computed in the RANS field
        """
        rans_file = DIR_MEAN / RANS_FILES[self.ID_MACH]
        rans_field_array = loadmat(rans_file)['arr']
        self.Nx, self.Nr, self.Nvalues = rans_field_array.shape # 536, 69, 8

        return {name: pd.DataFrame(rans_field_array[:, :, i], index=range(self.Nx), columns=range(self.Nr))
                for i, name in enumerate(rans_value_names)}

pert_field = perturbationField(St=0.4, ID_MACH=1)
rans_field = ransField(ID_MACH=1, St=0.4)
rans_values = rans_field.rans_values
rans_interpolated  = rans_field.interpolate_grid()
