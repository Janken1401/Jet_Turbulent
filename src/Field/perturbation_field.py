import pandas as pd
from matplotlib import ticker
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

from ReadData.read_radius import get_r_grid
from src.Field.rans_field import Ransfield
from src.toolbox.path_directories import DIR_STABILITY
from src.ReadData.read_info import get_reference_values
from src.toolbox.dimless_reference_values import *
from src.toolbox.fig_parameters import RANS_FIGSIZE


class Perturbationfield:
    pse_value_names = ['rho', 'ux', 'ur', 'ut', 'P']
    mean_titles = {'x': r'$\hat{x}$', 'r': r'$\hat{r}$', 'rho': r'$\hat{\rho}$',
              'ux': r'$\hat{u_x}$', 'ur': r'$\hat{u_\theta}$', 'ut': r'$\hat{u_\theta}$',
              'T': r'$\hat{T}$', 'P': r'$\hat{p}$'}

    def __init__(self, St=0.4, ID_MACH=1):
        if not isinstance(St, (int, float)):
            raise TypeError('St must be a float')
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')
        self.St = St
        self.ID_MACH = ID_MACH
        self.rans_field = Ransfield(ID_MACH)
        self.pert_values = self.get_perturbation_field()
        self.x_grid, self.r_grid = self.grid()
        self.mean_values = self.interpolate_to_pse_grid()

    def interpolate_to_pse_grid(self):
        rans_interpolated = {}
        rans_in_pse_ref = self.rans_field.convert_to_pse_reference()
        r_grid = get_r_grid()
        rans_x_values = [self.rans_field.values['x'].iloc[:, i] for i in range(len(r_grid))]

        for value in self.pse_value_names:
            #Making sure the interpolation is done for each points like this
            interpolated_field = np.zeros((len(self.x_grid), len(r_grid)))

            for i, r_val in enumerate(r_grid):
                rans_values_at_r = rans_in_pse_ref[value].iloc[:, i]
                rans_x_at_r = rans_x_values[i]

                cs = CubicSpline(rans_x_at_r, rans_values_at_r)

                interpolated_field[:, i] = cs(self.x_grid[:][i])

            rans_interpolated[value] = pd.DataFrame(interpolated_field)

        return rans_interpolated

    def convert_to_rans_reference(self):
        """
        Set the dimensionized RANS into the PSE reference system

        Returns
        -------
        rans_pse: dict
            contains DataFrame of the rans field in PSE reference system
        """

        pse_dim = self.dimensionalized()
        pse_to_rans = {
                'ux': pse_dim['ux'] / c_0,
                'ur': pse_dim['ur'] / c_0,
                'ut': pse_dim['ut'] / c_0,
                'T': pse_dim['T'] / ((gamma - 1) * T_0),
                'P': pse_dim['P'] / (gamma * p_0),
                'rho': pse_dim['rho'] / rho_0
        }

        return pse_to_rans

    def dimensionalized(self):
        """
        Re-dimensionalize the RANS field before set it to the PSE reference

        Returns
        -------
        rans_dim : dict
            contains DataFrame of the rans field except for x and r
        """
        ref_values = get_reference_values().iloc[self.ID_MACH - 1]
        rans_dim = {
                'ux': self.mean_values['ux'] * ref_values['ux'],
                'ur': self.mean_values['ur'] * ref_values['ux'],
                'ut': self.mean_values['ut'] * ref_values['ux'],
                'T': self.mean_values['T'] * ref_values['T'],
                'P': self.mean_values['P'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'rho': self.mean_values['rho'] * ref_values['rho']
        }

        return rans_dim

    def grid(self):
        nr = get_r_grid().size
        x = self.pert_values['x'].to_numpy()
        r_grid = pd.DataFrame(np.tile(get_r_grid(), (len(x), 1)))
        x_grid =  pd.DataFrame(np.tile(x[:, np.newaxis], (1, nr)))
        return x_grid, r_grid

    def plot(self, name_value, x_max=10, r_max=3):
        """

        Parameters
        ----------
        name_value: str
            value to plot. Avaible : 'ux', 'ur', 'ut', 'T', 'P'

        x_max: int or float - optional
        r_max: int or float - optional
            provide the limit of the domain to plot the values

        Returns
        -------
        None
        """
        if name_value not in self.pse_value_names:
            raise ValueError("Value is not in", self.pse_value_names)
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
        ax.set_title(self.mean_titles[name_value])
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
        x_mask = (self.x_grid.iloc[:, 0] >= 0) & (self.x_grid.iloc[:, 0] <= x_max)
        r_mask = (self.r_grid.iloc[0, :] >= 0) & (self.r_grid.iloc[0, :] <= r_max)
        value = self.mean_values[value]
        # Apply the masks to select the subarray
        x_sub = self.x_grid.loc[x_mask, r_mask]
        r_sub = self.r_grid.loc[x_mask, r_mask]
        value_sub = value.loc[x_mask, r_mask]
        return x_sub, r_sub, value_sub
    def get_perturbation_field(self):
        """Retrieve Results from stability fields

        Returns
        -------
        DataFrame
            a DataFrame containing all values from the perturbation field results
        """

        # Used read_csv instead with space delimiter instead of read_fwf in case
        # of floating inconsistency.
        dir_St = DIR_STABILITY / "St{:02d}".format(int(10 * self.St))
        dir_field = dir_St / 'Field' / f'FrancCase_{self.ID_MACH}'
        file_perturbation = dir_field / f'pertpse_FrancCase_{self.ID_MACH}.dat'

        return pd.read_csv(file_perturbation,
                           delimiter=r'\s+',
                           skiprows=3,
                           names=['x', 'r',
                                  'Re(ux)', 'Im(ux)', 'abs(ux)',
                                  'Re(ur)', 'Im(ur)', 'abs(ur)',
                                  'Re(ut)', 'Im(ut)', 'abs(ut)',
                                  'Re(rho)', 'Im(rho)', 'abs(rho)',
                                  'Re(p)', 'Im(p)', 'abs(p)']
                           )
