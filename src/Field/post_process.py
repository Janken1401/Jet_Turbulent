import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, ticker

from Field.perturbation_field import PerturbationField
from Field.stability import Stability
from toolbox.fig_parameters import RANS_FIGSIZE


class PostProcess:
    rans_value_names = ['rho', 'ux', 'ur', 'ut', 'p', 'T']
    pert_value_names = ['Re(ux)', 'Im(ux)', 'abs(ux)',
                        'Re(ur)', 'Im(ur)', 'abs(ur)',
                        'Re(rho)', 'Im(rho)', 'abs(rho)',
                        'Re(p)', 'Im(p)', 'abs(p)']

    titles = {'x': r'$\hat{x}$', 'r': r'$\hat{r}$', 'rho': r'$\hat{\rho}$',
              'ux': r'$\hat{u_x}$', 'ur': r'$\hat{u_r}$',
              'T': r'$\hat{T}$', 'p': r'$\hat{p}$'}
    titles.update({name: name for name in pert_value_names})

    def __init__(self, St, ID_MACH):
        self.pert_field = PerturbationField(St, ID_MACH)
        self.stability_data = Stability(St, ID_MACH).get_stability_data()
        self.rans_field = self.pert_field.rans_field
        self.rans_values = self.pert_field.rans_values
        self.x_grid = self.pert_field.x_grid
        self.r_grid = self.pert_field.r_grid

    def fields_stats(self):
        stats_dict = {}
        for field in self.rans_value_names:
            field_values = pd.Series(self.rans_field.interpolated_values[field].to_numpy().flatten())
            stats = field_values.describe()
            stats_dict[field] = stats
        return pd.DataFrame(stats_dict)

    def plot_alpha(self):
        fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        ax0.plot(self.x_grid, self.stability_data['Re(alpha)'], title=r'$\alpha_r$')
        ax1.plot(self.x_grid, self.stability_data['Im(alpha)'], title=r'$\alpha_i$')
        ax0.get_legend().remove()
        ax1.get_legend().remove()
        fig.tight_layout()
        plt.show()

    def plot(self, name_value, x_min=0, x_max=10, r_min=0, r_max=5, t=0):
        """

        Parameters
        ----------
        name_value: str
            value to plot. Available : -contourf : 'rho','ux', 'ur', 'T', 'P'
                                       -iso-contour : abs(q') and Re(q')

        x_max: int or float - optional
        r_max: int or float - optional
            provide the limit of the domain to plot the values

        Returns
        -------
        None
        """

        self.__test_validity_input_field(name_value, x_min, x_max, r_min, r_max)
        x, r, value = self.get_value_in_field(name_value, x_min=x_min, x_max=x_max, r_min=r_min, r_max=r_max)
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=RANS_FIGSIZE, layout='constrained')
        if name_value in self.rans_value_names:
            cs = ax.contourf(x, r, value.transpose(), levels=100, cmap='coolwarm')
        elif name_value in self.pert_value_names:
            cs = ax.contour(x, r, value.transpose(), levels=100, cmap='coolwarm')
        else:
            raise ValueError("Value can't be plotted")

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

    def get_value_in_field(self, name_value, x_min=0, x_max=10, r_min=0, r_max=3):
        """
        Return the value in the wanted domain

        Parameters
        ----------
        r_min
        x_min
        name_value: 'str'
            values to retrieve in the wanted domain.
            Value available : x, r, rho, ux, ur, T, p
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

        self.__test_validity_input_field(name_value, x_min, x_max, r_min, r_max)

        xmin_idx, xmax_idx, rmin_idx, rmax_idx = self.__get_index(x_min, x_max, r_min, r_max)
        # Apply the masks to select the subarray
        x_sub = self.pert_field.x_grid[xmin_idx: xmax_idx]
        r_sub = self.pert_field.r_grid[rmin_idx: rmax_idx]
        if name_value in self.rans_value_names:
            value = self.rans_values[name_value]
        elif name_value in self.pert_value_names:
            value = self.pert_field.values[name_value]
        else:
            raise ValueError("Value not available")
        value_sub = value.iloc[xmin_idx: xmax_idx, rmin_idx: rmax_idx]
        return x_sub, r_sub, value_sub

    def __test_validity_input_field(self, name_value, x_min, x_max, r_min, r_max):
        if name_value not in self.rans_value_names and name_value not in self.pert_value_names:
            raise ValueError("Value is not in", self.rans_value_names, self.pert_value_names)

        if not isinstance(x_max, (float, int)) or not isinstance(r_max, (float, int)):
            raise TypeError('x_max and r_max must be an int or a float')
        if not isinstance(x_min, (float, int)) or not isinstance(r_min, (float, int)):
            raise TypeError('x_min and r_min must be an int or a float')

        if x_max < x_min:
            raise ValueError('x_min must be greater than x_max')
        if r_max < r_min:
            raise ValueError('r_max must be greater than r_min')
        min_of_x = np.argmin(self.pert_field.x_grid)
        min_of_r = np.argmin(self.pert_field.r_grid)
        if x_min < min_of_x:
            raise ValueError(f'x_max must be greater than or equal to {min_of_x}')
        if r_min < min_of_r:
            raise ValueError(f'r_max must be greater than or equal to {min_of_r}')

        max_of_x = np.argmax(self.pert_field.x_grid)
        max_of_r = np.argmax(self.pert_field.r_grid)
        if x_min > max_of_x:
            raise ValueError(f'x_max must be greater than or equal to {max_of_x}')
        if r_min > max_of_r:
            raise ValueError(f'r_max must be greater than or equal to {max_of_r}')

    def __get_index(self, x_min, x_max, r_min, r_max):
        xmax_idx = np.where(self.pert_field.x_grid <= x_max)[0][-1]
        xmin_idx = np.where(self.pert_field.x_grid >= x_min)[0][0]
        rmax_idx = np.where(self.pert_field.r_grid <= r_max)[0][-1]
        rmin_idx = np.where(self.pert_field.r_grid >= r_min)[0][0]
        return xmin_idx, xmax_idx, rmin_idx, rmax_idx
