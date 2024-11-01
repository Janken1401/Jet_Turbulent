import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from ReadData.read_info import get_reference_values
from src.toolbox.path_directories import DIR_MEAN, RANS_FILES
from toolbox.fig_parameters import RANS_FIGSIZE
from src.toolbox.dimless_reference_values import gamma, rho_0, c_0, T_0, p_0


class Ransfield:
    titles = {'x': r'$\hat{x}$', 'r': r'$\hat{r}$', 'rho': r'$\hat{\rho}$',
              'ux': r'$\hat{u_x}$', 'ur': r'$\hat{u_\theta}$', 'ut': r'$\hat{u_\theta}$',
              'T': r'$\hat{T}$', 'P': r'$\hat{p}$'}
    names = ['x', 'r', 'rho', 'ux', 'ur', 'ut', 'T', 'P']

    def __init__(self, ID_MACH=1):
        """
        Parameters
        ----------
        ID_MACH : int
            ID of the Mach reference
        """
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')

        self.ID_MACH = ID_MACH
        self.values = self.get_rans_values()

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
        rans_dim = self.dimensionalized()
        rans_pse = {
                'ux': rans_dim['ux'] / u_ref,
                'ur': rans_dim['ur'] / u_ref,
                'ut': rans_dim['ut'] / u_ref,
                'T': rans_dim['T'] / ref_values['T'],
                'P': rans_dim['P'] / ref_values['P'],
                'rho': rans_dim['rho'] / ref_values['rho']
        }

        return rans_pse

    def dimensionalized(self):
        """
        Re-dimensionalize the RANS field before set it to the PSE reference

        Returns
        -------
        rans_dim : dict
            contains DataFrame of the rans field except for x and r
        """
        rans_values = self.get_rans_values()
        rans_dim = {
                'ux': rans_values['ux'] * c_0,
                'ur': rans_values['ur'] * c_0,
                'ut': rans_values['ut'] * c_0,
                'T': rans_values['T'] * (gamma - 1) * T_0,
                'P': rans_values['P'] * gamma * p_0,
                'rho': rans_values['rho'] * rho_0
        }

        return rans_dim

    def plot(self, name_value, x_max=10, r_max=3):
        """
        Parameters
        ----------
        name_value: str
            value to plot. Available : 'ux', 'ur', 'ut', 'T', 'P'
        x_max: int or float - optional
        r_max: int or float - optional
            provide the limit of the domain to plot the values

        Returns
        -------
        None
        """
        if name_value not in self.names:
            raise ValueError("Value is not in", self.names)
        if not isinstance(x_max, (int, float)) or not isinstance(r_max, (int, float)):
            raise TypeError('x_max and r_max must be an int or a float')

        x, r, value = self.get_value_in_field(name_value, x_max, r_max)
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=RANS_FIGSIZE, layout='constrained')
        cs = ax.contourf(x, r, value, levels=100, cmap='coolwarm')
        plt.xlabel('x/D')
        plt.ylabel('r/D')
        tick_spacing = 1
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax.set_title(self.titles[name_value])
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
        x_mask = (self.values['x'].iloc[:, 0] >= 0) & (self.values['x'].iloc[:, 0] <= x_max)
        r_mask = (self.values['r'].iloc[0, :] >= 0) & (self.values['r'].iloc[0, :] <= r_max)
        value = self.values[value]
        # Apply the masks to select the subarray
        x_sub = self.values['x'].loc[x_mask, r_mask]
        r_sub = self.values['r'].loc[x_mask, r_mask]
        value_sub = value.loc[x_mask, r_mask]
        return x_sub, r_sub, value_sub

    def get_rans_values(self):
        """
        Retrieve values of the RANS mean field based on the mach case selected

        Returns
        -------
        Dict: a dict containing DataFrame for each value computed in the RANS field
        """
        rans_file = DIR_MEAN / RANS_FILES[self.ID_MACH]
        rans_field_array = loadmat(rans_file)['arr']
        Nx, Nr, Nvalues = rans_field_array.shape  # 536, 69, 8
        return {name: pd.DataFrame(rans_field_array[:, :, i], index=range(Nx), columns=range(Nr))
                for i, name in enumerate(self.names)}
