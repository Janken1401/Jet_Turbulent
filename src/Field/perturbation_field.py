import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy.interpolate import CubicSpline

from ReadData.read_mach import get_mach_reference
from ReadData.read_radius import get_r_grid
from src.Field.rans_field import RansField
from src.toolbox.path_directories import DIR_STABILITY
from src.ReadData.read_info import get_reference_values
from src.toolbox.dimless_reference_values import c_0, p_0, T_0, rho_0, gamma, R


class PerturbationField:
    rans_quantities = ['rho', 'ux', 'ur', 'ut', 'p', 'T']

    pse_quantities = ['x', 'r',
                      'Re(rho)', 'Im(rho)', 'abs(rho)',
                      'Re(ux)', 'Im(ux)', 'abs(ux)',
                      'Re(ur)', 'Im(ur)', 'abs(ur)',
                      'Re(ut)', 'Im(ut)', 'abs(ut)',
                      'Re(p)', 'Im(p)', 'abs(p)',
                      'Re(T)', 'Im(T)', 'abs(T)']

    stability_quantities = ['x',
                            'Re(alpha)', 'Im(alpha)', 'abs(alpha)',
                            'Re(int(alpha))', 'Im(int(alpha))',
                            'C<sub>ph</sub>', 'sigma', 'N']

    def __init__(self, St: float, ID_MACH: int, verbose: bool = False) -> None:
        """

        Parameters
        ----------
        St: int or float
            Strouhal Number
        ID_MACH: int
            Case selected
        """
        if not isinstance(St, (int, float)) or St <= 0:
            raise ValueError('St must be a positive float or integer')
        if not isinstance(ID_MACH, int) or ID_MACH <= 0:
            raise ValueError('ID_MACH must be a positive integer')

        self.x_grid = None
        self.values = None
        self.St = St
        self.ID_MACH = ID_MACH
        self.__get_raw_perturbation_values()
        self.rans_values = self.interpolate()


    def compute_total_field(self, t: [int, float] = 0, epsilon_q: [int, float] = 0.01, ):
        q_tot = {}
        q_prime = self.compute_perturbation_field(t_percent_T=t)
        q_prime = self.convert_to_rans_reference()
        for rans_quantity in self.rans_quantities:
            q_tot[rans_quantity] = self.rans_values[rans_quantity] + epsilon_q * np.real(q_prime[rans_quantity])

        return q_tot

    def compute_perturbation_field(self, t_percent_T: [int, float] = 0) -> dict[str, pd.DataFrame]:

        if not isinstance(t_percent_T, (int, float)) or t_percent_T < 0 or t_percent_T > 100:
            raise ValueError('t_percent_T must be a positive integer between 0 and 100')

        q_prime = {}
        stability_data = self.get_stability_data()
        theta_real = stability_data['Re(int(alpha))']
        theta_imag = stability_data['Im(int(alpha))']

        T = 2 * np.pi / self.St
        t = t_percent_T * T / 100

        f = lambda time: np.exp(-theta_imag) * np.exp(1j * theta_real - self.St * time)

        # Retrieve the real and imaginary values of the pse field associated with the rans field quantity
        # e.g: ux: [Re(ux), Im(ux)]
        rans_pse_quantities = {rans_quantity: [pse_quantity for pse_quantity in self.pse_quantities
                                               if (rans_quantity in pse_quantity) and 'abs' not in pse_quantity]
                               for rans_quantity in self.rans_quantities}

        for rans_quantity, pse_parts in rans_pse_quantities.items():
            real_value = self.values[pse_parts[0]]
            imag_value = self.values[pse_parts[1]]
            q_prime[rans_quantity] = (real_value + 1j * imag_value)

        for rans_quantity in self.rans_quantities:
            q_prime[rans_quantity] = q_prime[rans_quantity].mul(f(t), axis='index')

        return q_prime

    @classmethod
    def convert_to_rans_reference(self, pse_dim) -> dict[str, pd.DataFrame]:
        """
        Set the dimensionized RANS into the PSE reference system

        Returns
        -------
        rans_pse: dict
            contains DataFrame of the rans field in PSE reference system
        """

        pse_to_rans = {
                'Re(ux)': pse_dim['Re(ux)'] / c_0,
                'Im(ux)': pse_dim['Im(ux)'] / c_0,
                'abs(ux)': pse_dim['abs(ux)'] / c_0,

                'Re(ur)': pse_dim['Re(ur)'] / c_0,
                'Im(ur)': pse_dim['Im(ur)'] / c_0,
                'abs(ur)': pse_dim['abs(ur)'] / c_0,

                'Re(ut)': pse_dim['Re(ur)'] / c_0,
                'Im(ut)': pse_dim['Im(ut)'] / c_0,
                'abs(ut)': pse_dim['abs(ut)'] / c_0,

                'Re(rho)': pse_dim['Re(rho)'] / c_0,
                'Im(rho)': pse_dim['Im(rho)'] / rho_0,
                'abs(rho)': pse_dim['abs(rho)'] / c_0,

                'Re(p)': pse_dim['Re(p)'] / (gamma * p_0),
                'Im(p)': pse_dim['Im(p)'] / (gamma * p_0),
                'abs(p)': pse_dim['abs(p)'] / (gamma * p_0),

                'abs(T)': pse_dim['abs(T)'] * (gamma - 1) * T_0,
                'Re(T)': pse_dim['Re(T)'] * (gamma - 1) * T_0,
                'Im(T)': pse_dim['Im(T)'] * (gamma - 1) * T_0,
        }

        return pse_to_rans

    @classmethod
    def pse_dimensionalized(self, dimless_pse) -> dict[str, pd.DataFrame]:
        """
        Re-dimensionalize the RANS field before set it to the PSE reference

        Returns
        -------
        rans_dim : dict
            contains DataFrame of the rans field except for x and r
        """
        ref_values = get_reference_values().iloc[self.ID_MACH]
        pse_dim = {
                'abs(ux)': dimless_pse['abs(ux)'] * ref_values['ux'],
                'Re(ux)': dimless_pse['Re(ux)'] * ref_values['ux'],
                'Im(ux)': self.values['Im(ux)'] * ref_values['ux'],

                'abs(ur)': self.values['abs(ur)'] * ref_values['ux'],
                'Re(ur)': self.values['Re(ur)'] * ref_values['ux'],
                'Im(ur)': self.values['Im(ur)'] * ref_values['ux'],

                'abs(ut)': self.values['abs(ut)'] * ref_values['ux'],
                'Re(ut)': self.values['Re(ut)'] * ref_values['ux'],
                'Im(ut)': self.values['Im(ut)'] * ref_values['ux'],

                'abs(p)': self.values['abs(p)'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'Re(p)': self.values['Re(p)'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'Im(p)': self.values['Im(p)'] * ref_values['rho'] * ref_values['ux'] ** 2,

                'abs(rho)': self.values['abs(rho)'] * ref_values['rho'],
                'Re(rho)': self.values['Re(rho)'] * ref_values['rho'],
                'Im(rho)': self.values['Im(rho)'] * ref_values['rho'],

                'abs(T)': self.values['abs(T)'] * ref_values['T'],
                'Re(T)': self.values['Re(T)'] * ref_values['T'],
                'Im(T)': self.values['Im(T)'] * ref_values['T'],
        }

        return pse_dim

    def interpolate(self) -> dict[str, pd.DataFrame]:
        """
        Interpolate the RANS values to the PSE grid and update the RANS values directly.

        """
        rans_field = RansField(self.ID_MACH)
        r_grid = get_r_grid()
        rans_interpolated = {}
        for value in self.rans_quantities:
            field = np.zeros((len(self.x_grid), len(r_grid)))

            for i, r_val in enumerate(r_grid):
                rans_values_at_r = rans_field.values[value].iloc[:, i]

                cs = CubicSpline(rans_field.x, rans_values_at_r)

                field[:, i] = cs(self.x_grid)

            rans_interpolated[value] = pd.DataFrame(field)

        return rans_interpolated

    def __get_raw_perturbation_values(self):
        """Retrieve Results from stability fields as a dictionary of DataFrames with integer indexing.

        Returns
        -------
        dict
            A dictionary where each key is a quantity name and the value is a DataFrame
            with integer indices for rows (x-axis) and columns (r-axis).
        """

        dir_st = DIR_STABILITY / f"St{int(10 * self.St):02d}"
        dir_field = dir_st / 'Field' / f'FrancCase_{self.ID_MACH}'
        file_perturbation = dir_field / f'pertpse_FrancCase_{self.ID_MACH}.dat'
        if file_perturbation.exists():
            full_data = pd.read_csv(
                    file_perturbation,
                    delimiter=r'\s+',
                    skiprows=3,
                    names=self.pse_quantities
            )
        else:
            raise ValueError('No stability field found - The Strouhal Number you have entered might not be available.')
        # compute T according to perfect gas low
        full_data['Re(T)'] = full_data['Re(p)'] / (full_data['Re(rho)'] * R)
        full_data['Im(T)'] = full_data['Im(p)'] / (full_data['Im(rho)'] * R)
        full_data['abs(T)'] = full_data['abs(p)'] / (full_data['abs(rho)'] * R)

        x_values = full_data['x'].unique()
        nx = range(len(x_values))
        nr = range(len(get_r_grid()))
        perturbation_dict = {}

        for quantity in self.pse_quantities[2:]:
            # Pivot and reset index and columns to integers
            quantity_df = full_data.pivot(index='x', columns='r', values=quantity)
            quantity_df.index = nx
            quantity_df.columns = nr
            perturbation_dict[quantity] = quantity_df

        self.values = perturbation_dict
        self.x_grid = x_values

    def get_stability_data(self) -> DataFrame:
        """Retrieve Results from stability fields

        Returns
        -------
        DataFrame
            a DataFrame containing all values from the perturbation field results
        """

        # Used read_csv instead with space delimiter instead of read_fwf in case
        # of floating inconsistency.

        dir_st = DIR_STABILITY / "St{:02d}".format(int(10 * self.St))
        dir_field = dir_st / 'alpha' / f'FrancCase_{self.ID_MACH}'
        file_stability = dir_field / f'vappse_FrancCase_{self.ID_MACH}.dat'

        if not file_stability.exists():
            raise ValueError('File not found - The Strouhal Number you have entered might not be available.')

        return pd.read_csv(file_stability,
                           delimiter=r'\s+',
                           skiprows=3,
                           names=self.stability_quantities).drop(labels=['x', 'C<sub>ph</sub>', 'sigma', 'N'],
                                                                 axis='columns')
