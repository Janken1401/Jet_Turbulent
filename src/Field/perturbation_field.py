import pandas as pd
from matplotlib import ticker
from pandas import DataFrame
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

from ReadData.read_radius import get_r_grid
from src.Field.rans_field import RansField
from src.toolbox.path_directories import DIR_STABILITY
from src.ReadData.read_info import get_reference_values
from src.toolbox.dimless_reference_values import *


class PerturbationField:
    pse_value_names = ['x', 'r',
                       'Re(ux)', 'Im(ux)', 'abs(ux)',
                       'Re(ur)', 'Im(ur)', 'abs(ur)',
                       'Re(ut)', 'Im(ut)', 'abs(ut)',
                       'Re(rho)', 'Im(rho)', 'abs(rho)',
                       'Re(p)', 'Im(p)', 'abs(p)']

    def __init__(self, St=0.4, ID_MACH=1):
        """

        Parameters
        ----------
        St: int or float
            Strouhal Number
        ID_MACH: int
            Case selected
        """
        if not isinstance(St, (int, float)):
            raise TypeError('St must be a float')
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')
        self.St = St
        self.ID_MACH = ID_MACH
        self.rans_field = RansField(self.ID_MACH)
        self.pert_values = self.get_perturbation_values()
        self.x_grid, self.r_grid = self.grid()
        self.rans_field.interpolate(self.x_grid)
        self.rans_values = self.rans_field.interpolated_values

    def convert_to_rans_reference(self):
        """
        Set the dimensionized RANS into the PSE reference system

        Returns
        -------
        rans_pse: dict
            contains DataFrame of the rans field in PSE reference system
        """

        pse_dim = self.pse_dimensionalized()
        pse_to_rans = {
                'abs(ux)': pse_dim['abs(ux)'] / c_0,
                'Re(ux)': pse_dim['Re(ux)'] / c_0,
                'Im(ux)': pse_dim['Im(ux)'] / c_0,
                'abs(ur)': pse_dim['abs(ur)'] / c_0,
                'Re(ur)': pse_dim['Re(ur)'] / c_0,
                'Im(ur)': pse_dim['Im(ur)'] / c_0,
                'abs(rho)': pse_dim['abs(rho)'] / c_0,
                'Re(rho)': pse_dim['Re(rho)'] / c_0,
                'Im(rho)': pse_dim['Im(rho)'] / rho_0,
                'abs(p)': pse_dim['abs(p)'] / (gamma * p_0),
                'Re(p)': pse_dim['Re(p)'] / (gamma * p_0),
                'Im(p)': pse_dim['Im(p)'] / (gamma * p_0),
        }

        return pse_to_rans

    def pse_dimensionalized(self):
        """
        Re-dimensionalize the RANS field before set it to the PSE reference

        Returns
        -------
        rans_dim : dict
            contains DataFrame of the rans field except for x and r
        """
        ref_values = get_reference_values().iloc[self.ID_MACH - 1]
        pse_dim = {
                'abs(ux)': self.pert_values['abs(ux)'] * ref_values['ux'],
                'Re(ux)': self.pert_values['Re(ux)'] * ref_values['ux'],
                'Im(ux)': self.pert_values['Im(ux)'] * ref_values['ux'],
                'abs(ur)': self.pert_values['abs(ur)'] * ref_values['ux'],
                'Re(ur)': self.pert_values['Re(ur)'] * ref_values['ux'],
                'Im(ur)': self.pert_values['Im(ur)'] * ref_values['ux'],
                'abs(p)': self.pert_values['abs(p)'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'Re(p)': self.pert_values['Re(p)'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'Im(p)': self.pert_values['Im(p)'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'abs(rho)': self.pert_values['abs(rho)'] * ref_values['rho'],
                'Re(rho)': self.pert_values['Re(rho)'] * ref_values['rho'],
                'Im(rho)': self.pert_values['Im(rho)'] * ref_values['rho']
        }

        return pse_dim

    def get_interpolated_values(self, x_grid):
        return self.rans_field.interpolate(x_grid=x_grid)

    def grid(self):
        nr = get_r_grid().size
        x = self.pert_values['x'].to_numpy()
        r_grid = pd.DataFrame(np.tile(get_r_grid(), (len(x), 1)))
        x_grid = pd.DataFrame(np.tile(x[:, np.newaxis], (1, nr)))
        return x_grid, r_grid

    def get_perturbation_values(self):
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
                           names=self.pse_value_names
                           )
