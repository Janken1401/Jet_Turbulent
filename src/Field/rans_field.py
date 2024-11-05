import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.io import loadmat

from ReadData.read_info import get_reference_values
from ReadData.read_radius import get_r_grid
from src.toolbox.path_directories import DIR_MEAN, RANS_FILES
from src.toolbox.dimless_reference_values import gamma, rho_0, c_0, T_0, p_0


class RansField:
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
        self.get_rans_values()

    def interpolate(self, x_grid) :
        """
        Interpolate the RANS values to the PSE grid and update the RANS values directly.

        Parameters
        ----------
        x_grid: np.ndarray
            The grid of x values for interpolation.
.
        """
        # if not isinstance(x_grid, pd.DataFrame):
        #     raise TypeError('x_grid must be a np.ndarray')
        # if np.shape(x_grid)[0] <= np.shape(self.values['x'])[0]:
        #     raise ValueError('Values must be interpolated into a larger grid')
        # if np.shape(x_grid)[1] != np.shape(self.values['x'])[1]:
        #     raise ValueError('the grid along r must have the same size')

        rans_interpolated = {}
        r_grid = get_r_grid()
        for value in self.names[2:]: #skip x and r
            field = np.zeros((len(x_grid), len(r_grid)))

            for i, r_val in enumerate(r_grid):
                rans_values_at_r = self.values[value].iloc[:, i]

                cs = CubicSpline(self.x, rans_values_at_r)

                field[:, i] = cs(x_grid)

            rans_interpolated[value] = pd.DataFrame(field, index=x_grid, columns=r_grid)

        self.interpolated_values = rans_interpolated



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
        self.x = rans_field_array[:, 0, 0]
        return {name: pd.DataFrame(rans_field_array[:, :, i+2], index=range(Nx), columns=range(Nr))
                for i, name in enumerate(self.names[2:])} #skip x and r
