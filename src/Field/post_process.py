import pandas as pd
from matplotlib import pyplot as plt, ticker

from Field.perturbation_field import PerturbationField
from Field.stability import Stability
from toolbox.fig_parameters import RANS_FIGSIZE


class PostProcess:
    rans_value_names = ['rho', 'ux', 'ur', 'P', 'T']
    pert_value_names = ['Re(ux)', 'Im(ux)', 'abs(ux)',
                        'Re(ur)', 'Im(ur)', 'abs(ur)',
                        'Re(rho)', 'Im(rho)', 'abs(rho)',
                        'Re(p)', 'Im(p)', 'abs(p)']

    titles = {'x': r'$\hat{x}$', 'r': r'$\hat{r}$', 'rho': r'$\hat{\rho}$',
              'ux': r'$\hat{u_x}$', 'ur': r'$\hat{u_r}$',
              'T': r'$\hat{T}$', 'P': r'$\hat{p}$'}

    def __init__(self, St, ID_MACH):
        self.pert_field = PerturbationField(St, ID_MACH)
        self.pert_values = self.pert_field.get_perturbation_values()
        self.rans_field = self.pert_field.rans_values
        self.stability_data = Stability(St, ID_MACH).get_stability_data()
        self.x_grid, self.r_grid = self.pert_field.grid()

    def fields_stats(self):
        stats_dict = {}
        for field in self.rans_value_names:
            field_values = pd.Series(self.rans_field.interpolated_values[field].values.flatten())
            stats = field_values.describe()
            stats_dict[field] = stats
        return pd.DataFrame(stats_dict)

    def plot_alpha(self):
        fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        self.stability_data.plot(x='x', y='Re(alpha)', ax=ax0, title=r'$\alpha_r$')
        self.stability_data.plot(x='x', y='Im(alpha)', ax=ax1, title=r'$\alpha_i$')
        ax0.get_legend().remove()
        ax1.get_legend().remove()
        fig.tight_layout()
        plt.show()

    def plot(self, name_value, x_min=0, x_max=10, r_min=0, r_max=3):
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
        if name_value not in self.rans_value_names and name_value not in self.pert_value_names:
            raise ValueError("Value is not in", self.rans_value_names, self.pert_value_names)
        if not isinstance(x_max, (int, float)) or not isinstance(r_max, (int, float)):
            raise TypeError('x_max and r_max must be an int or a float')
        if not isinstance(x_min, (int, float)) or not isinstance(r_min, (int, float)):
            raise TypeError('x_min and r_min must be an int or a float')

        if x_max <= x_min:
            raise ValueError("x_max must be greater than x_min")
        if x_min < 0 or x_max > 20:
            raise ValueError("x_min and x_max must be between 0 and 20")
        if r_max <= r_min:
            raise ValueError("r_max must be greater than r_min")
        if r_min < 0 or r_max > 20:
            raise ValueError("r_min and r_max must be between 0 and 20")

        x, r, value = self.get_value_in_field(name_value, x_min=x_min, x_max=x_max, r_min=r_min, r_max=r_max)
        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=RANS_FIGSIZE, layout='constrained')
        if name_value in self.rans_value_names:
            cs = ax.contourf(x, r, value, levels=100, cmap='coolwarm')
        elif name_value in self.pert_value_names:
            cs = ax.contour(x, r, value, levels=100, cmap='coolwarm')
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

        if name_value not in self.rans_value_names and name_value not in self.pert_value_names:
            raise ValueError("Value is not in", self.rans_value_names, self.pert_value_names)
        if not isinstance(x_max, (int, float)) or not isinstance(r_max, (int, float)):
            raise TypeError('x_max and r_max must be an int or a float')
        if not isinstance(x_min, (int, float)) or not isinstance(r_min, (int, float)):
            raise TypeError('x_min and r_min must be an int or a float')

        if x_max <= x_min:
            raise ValueError("x_max must be greater than x_min")
        if x_min < 0 or x_max > 20:
            raise ValueError("x_min and x_max must be between 0 and 20")
        if r_max <= r_min:
            raise ValueError("r_max must be greater than r_min")
        if r_min < 0 or r_max > 20:
            raise ValueError("r_min and r_max must be between 0 and 20")

        x_mask = (self.x_grid.iloc[:, 0] >= x_min) & (self.x_grid.iloc[:, 0] <= x_max)
        r_mask = (self.r_grid.iloc[0, :] >= r_min) & (self.r_grid.iloc[0, :] <= r_max)
        value = self.rans_field[name_value]
        # Apply the masks to select the subarray
        x_sub = self.x_grid.loc[x_mask, r_mask]
        r_sub = self.r_grid.loc[x_mask, r_mask]
        value_sub = value.loc[x_mask, r_mask]
        return x_sub, r_sub, value_sub
