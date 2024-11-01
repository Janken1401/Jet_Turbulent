import pandas as pd
from scipy.interpolate import CubicSpline

from ReadData.read_radius import get_r_grid
from src.Field.rans_field import ransField
from src.toolbox.path_directories import DIR_STABILITY
from src.ReadData.read_info import get_reference_values
from src.toolbox.dimless_reference_values import *

pse_value_names = ['rho', 'ux', 'ur', 'ut', 'P']


class perturbationField:
    def __init__(self, St=0.4, ID_MACH=1):
        if not isinstance(St, (int, float)):
            raise TypeError('St must be a float')
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')
        self.St = St
        self.ID_MACH = ID_MACH
        self.rans_field = ransField(ID_MACH)
        self.pse_values = self.get_perturbation_field()
        # self.x_grid, self.r_grid = self.grid()

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
        # Initialize dictionary to store interpolated values
        rans_interpolated = {}
        rans_field = ransField(self.ID_MACH)
        rans_values = rans_field.convert_to_pse_reference()

        rans_x_grid = rans_values['x'].to_numpy()[]


        for value in pse_value_names:
            # Initialize an empty array for interpolated values on the PSE grid
            interpolated_field = np.zeros((len(self.x_grid), len(self.r_grid)))

            # Interpolate along the x-axis for each fixed r value (since r grids match)
            for i, r_val in enumerate(self.r_grid):
                # Interpolate at this r position across all x values
                rans_values_at_x = rans_values[value].iloc[:, i]
                cs = CubicSpline(rans_x_grid, rans_values_at_x)
                interpolated_field[:, i] = cs(self.x_grid)

                rans_interpolated[value] = pd.DataFrame(interpolated_field,
                                                        index=self.x_grid, columns=self.r_grid)

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
        pert_values = self.get_perturbation_field()
        ref_values = get_reference_values().iloc[self.ID_MACH - 1]
        rans_dim = {
                'ux': pert_values['ux'] * ref_values['ux'],
                'ur': pert_values['ur'] * ref_values['ux'],
                'ut': pert_values['ut'] * ref_values['ux'],
                'T': pert_values['T'] * ref_values['T'],
                'P': pert_values['P'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'rho': pert_values['rho'] * ref_values['rho']
        }

        return rans_dim

    def grid(self):
        x_grid = self.get_perturbation_field()['x'].to_numpy()
        r_grid = get_r_grid()
        nx = len(np.unique(x_grid))
        nr = len(r_grid)
        df_x_grid = pd.DataFrame(x_grid.reshape(nx, nr), columns=np.arange(nr))
        df_r_grid = pd.DataFrame(r_grid.reshape(nx, nr), columns=np.arange(nr))
        return df_x_grid, df_r_grid

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
