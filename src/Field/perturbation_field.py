import pandas as pd
from scipy.interpolate import CubicSpline, griddata, interpn

from ReadData.read_radius import get_r_grid
from src.Field.rans_field import ransField
from src.toolbox.path_directories import DIR_STABILITY
from src.ReadData.read_info import get_reference_values
from src.toolbox.dimless_reference_values import *


class perturbationField:
    pse_value_names = ['rho', 'ux', 'ur', 'ut', 'P']
    r_grid = get_r_grid()

    def __init__(self, St=0.4, ID_MACH=1):
        if not isinstance(St, (int, float)):
            raise TypeError('St must be a float')
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')
        self.St = St
        self.ID_MACH = ID_MACH
        self.rans_field = ransField(ID_MACH)
        self.values = self.get_perturbation_field()
        self.pse_grid = self.grid()

    # def interpolate_grid(self):
    #     rans_values = self.rans_field.convert_to_pse_reference()
    #     rans_x_grid = self.rans_field.get_x_grid()
    #     pse_x_grid = self.get_perturbation_field()['x']
    #     r_grid = get_r_grid()
    #     Nr = len(r_grid)
    #     rans_interpolated = {}
    #
    #     for var_name in ('ux', 'ur', 'ut', 'rho', 'T', 'P'):
    #         interpolated_grid = np.zeros((len(pse_x_grid), Nr))
    #
    #         for i, r_point in enumerate(r_grid):
    #             rans_values_at_x = rans_values[var_name].iloc[:, i]
    #             spline = CubicSpline(rans_x_grid, rans_values_at_x)
    #             interpolated_grid[:, i] = spline(pse_x_grid)
    #
    #         rans_interpolated[var_name] = pd.DataFrame(interpolated_grid,
    #                                                        index=pse_x_grid, columns=r_grid)
    #
    #     return rans_interpolated


    def interpolate_to_pse_grid(self):
        rans_interpolated = {}
        rans_field = ransField(self.ID_MACH)
        rans_in_pse_ref = rans_field.convert_to_pse_reference()

        rans_x_values = [rans_field.values['x'].iloc[:, i] for i in range(len(self.r_grid))]

        for value in self.pse_value_names:
            #Making sure the interpolation is done for each points like this
            interpolated_field = np.zeros((len(self.pse_grid), len(self.r_grid)))

            for i, r_val in enumerate(self.r_grid):
                rans_values_at_r = rans_in_pse_ref[value].iloc[:, i]
                rans_x_at_r = rans_x_values[i]

                cs = CubicSpline(rans_x_at_r, rans_values_at_r)

                interpolated_field[:, i] = cs(self.pse_grid[:, i])

            rans_interpolated[value] = interpolated_field

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
                'ux': self.values['ux'] * ref_values['ux'],
                'ur': self.values['ur'] * ref_values['ux'],
                'ut': self.values['ut'] * ref_values['ux'],
                'T': self.values['T'] * ref_values['T'],
                'P': self.values['P'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'rho': self.values['rho'] * ref_values['rho']
        }

        return rans_dim

    def grid(self):
        nr = self.r_grid.size
        x = self.values['x'].to_numpy()
        return np.tile(x[:, np.newaxis], (1, nr))

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
