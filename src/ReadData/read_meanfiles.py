import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from src.toolbox.path_directories import DIR_MEAN, RANS_FILES
from toolbox.fig_parameters import RANS_FIGSIZE
from src.ReadData.read_mach import get_mach_reference

rans_value_names = ['x', 'r', 'rho', 'ux', 'ur', 'ut', 'T', 'p']


class ransField:
    def __init__(self, ID_MACH):
        """

        Parameters
        ----------
        ID_MACH
        """
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')

        self.ID_MACH = ID_MACH
        rans_file = DIR_MEAN / RANS_FILES[self.ID_MACH]

        self.mach = get_mach_reference().loc[self.ID_MACH - 1]
        self.rans_field_array = loadmat(rans_file)['arr']
        self.Nx, self.Nr, self.Nvalues = self.rans_field_array.shape # 536, 69, 8
        self.rans_field = self._get_rans_field()
        self.x = self.rans_field['x']
        self.r = self.rans_field['r']

    def plot_mean_value(self, value, x_max=10, r_max=3):
        if value not in self.rans_field.keys():
            raise ValueError('value must be either x, r, rho, ux, ur, ut, T or p')
        if not isinstance(x_max, (int, float)) or not isinstance(r_max, (int, float)):
            raise TypeError('x_max and r_max must be an int or a float')

        titles = {'x': r'$\hat{x}$', 'r': r'$\hat{r}$', 'rho': r'$\hat{\rho}$',
                  'ux': r'$\hat{u_x}$', 'ur': r'$\hat{u_\theta}$', 'ut': r'$\hat{u_\theta}$',
                  'T': r'$\hat{T}$', 'P': r'$\hat{p}$'}

        self.plot_value_in_field(value, titles[value], x_max, r_max)

    def plot_value_in_field(self, value, title='', x_max=10, r_max=3):
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
        value: DataFrame
            values to retrieve in the wanted domain.
            Value available : x, r, rho, ux, ur, ut, T, p, Ma
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
        x_mask = (self.x.iloc[:, 0] >= 0) & (self.x.iloc[:, 0] <= x_max)
        r_mask = (self.r.iloc[0, :] >= 0) & (self.r.iloc[0, :] <= r_max)
        value = self.rans_field[value]
        # Apply the masks to select the subarray
        x_sub = self.x.loc[x_mask, r_mask].values
        r_sub = self.r.loc[x_mask, r_mask].values
        value_sub = value.loc[x_mask, r_mask].values
        return pd.DataFrame(x_sub), pd.DataFrame(r_sub), pd.DataFrame(value_sub)

    def _get_rans_field(self):
        """
        Retrieve values of the RANS mean field based on the mach case selected

        Returns
        -------
        Dict: a dict containing DataFrame for each value computed in the RANS field
        """
        return {name: pd.DataFrame(self.rans_field_array[:, :, i], index=range(self.Nx), columns=range(self.Nr))
                for i, name in enumerate(rans_value_names)}
