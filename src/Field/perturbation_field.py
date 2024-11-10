import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy.interpolate import CubicSpline

from src.ReadData.read_radius import get_r_grid
from src.Field.rans_field import RansField
from src.toolbox.path_directories import DIR_STABILITY
from src.ReadData.read_info import get_reference_values
from src.toolbox.dimless_reference_values import c_0, p_0, rho_0, gamma


class PerturbationField:
    rans_quantities = ['rho', 'ux', 'ur', 'ut', 'p']

    pse_quantities = ['x', 'r',
                      'Re(ux)', 'Im(ux)', 'abs(ux)',
                      'Re(ur)', 'Im(ur)', 'abs(ur)',
                      'Re(ut)', 'Im(ut)', 'abs(ut)',
                      'Re(rho)', 'Im(rho)', 'abs(rho)',
                      'Re(p)', 'Im(p)', 'abs(p)',
                      ]

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
            raise ValueError('St must be a positive number')
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
        q_prime = self.convert_to_rans_reference(q_prime, self.ID_MACH)
        for rans_quantity in self.rans_quantities:
            q_tot[rans_quantity] = self.rans_values[rans_quantity] + epsilon_q * np.real(q_prime[rans_quantity])

        return q_tot

    def compute_perturbation_field(self, t_percent_T: [int, float] = 0) -> dict[str, pd.DataFrame]:
        """
        Computes the complex perturbation fields for each RANS quantity with a time-dependent function applied.

        Parameters
        ----------
        t_percent_T : int or float, optional
            Time as a percentage of the fundamental period T (must be between 0 and 100). Defaults to 0.

        Returns
        -------
        dict[str, pd.DataFrame]
            A dictionary containing the computed complex perturbation fields for each RANS quantity.
        """
        if not isinstance(t_percent_T, (int, float)) or not (0 <= t_percent_T <= 100):
            raise ValueError("t_percent_T must be a positive number between 0 and 100.")

        # Retrieve stability data for the computation of the time-dependent factor
        stability_data = self.get_stability_data()
        theta_real = stability_data['Re(int(alpha))']
        theta_imag = stability_data['Im(int(alpha))']

        # Calculate the time variable based on the percentage of the period T
        T = 2 * np.pi / self.St
        t = (t_percent_T / 100) * T

        # Define the time-dependent multiplier function
        time_multiplier = np.exp(-theta_imag) * np.exp(1j * (theta_real - self.St * t))

        # Map each RANS field quantity to its real and imaginary PSE field components
        rans_pse_quantities = {
                rans_quantity: [
                        pse_quantity for pse_quantity in self.pse_quantities[2:]
                        if rans_quantity in pse_quantity and 'abs' not in pse_quantity
                ]
                for rans_quantity in self.rans_quantities
        }

        q_prime = {}

        for rans_quantity, pse_parts in rans_pse_quantities.items():
            real_part = self.values[pse_parts[0]]
            imag_part = self.values[pse_parts[1]]

            q_prime[rans_quantity] = real_part + 1j * imag_part

        for rans_quantity in q_prime:
            q_prime[rans_quantity] = q_prime[rans_quantity].mul(time_multiplier, axis='index')

        return q_prime

    @staticmethod
    def convert_to_rans_reference(dimless_field: dict[str, pd.DataFrame], ID_MACH: int) -> dict[str, pd.DataFrame]:
        """
        Convert a dimensionless RANS field to the PSE reference system, handling both combined quantities
        (e.g., 'ux') and component quantities (e.g., 'abs(ux)', 'Re(ux)', 'Im(ux)') in a unified manner.

        Parameters
        ----------
        dimless_field : dict[str, pd.DataFrame]
            A dictionary containing DataFrames of the dimensionless RANS field values.
        ID_MACH : int
            The ID of the Mach case for retrieving reference values.

        Returns
        -------
        dict[str, pd.DataFrame]
            A dictionary of the dimensionalized RANS field in the PSE reference system.
        """
        conversion_factors = {
                'ux': c_0,
                'ur': c_0,
                'ut': c_0,
                'p': gamma * p_0,
                'rho': rho_0
        }
        ref_values = get_reference_values().iloc[ID_MACH - 1]

        scaling_factors = {
                'ux': ref_values['ux'],
                'ur': ref_values['ux'],
                'ut': ref_values['ux'],
                # 'p': ref_values['rho'] * (ref_values['ux'] ** 2),
                'p': ref_values['P'],
                'rho': ref_values['rho']
        }

        # pse_dim = PerturbationField.pse_dimensionalized(dimless_field, ID_MACH)
        pse_to_rans = {}
        for key in dimless_field:
            for (quantity_1, conv_factor), (quantity_2, scale_factor) in zip(conversion_factors.items(), scaling_factors.items()):
                if quantity_1 in key:
                    pse_to_rans[key] = dimless_field[key] * (scale_factor / conv_factor)
                    # pse_to_rans[key] = dimless_field[key]  / conv_factor
                    break

        return pse_to_rans

    # @staticmethod
    # def pse_dimensionalized(dimless_pse: dict[str, pd.DataFrame], ID_MACH: int) -> dict[str, pd.DataFrame]:
    #     """
    #     Re-dimensionalize the PSE field using reference values, handling both combined and component quantities.
    #
    #     Parameters
    #     ----------
    #     dimless_pse : dict[str, pd.DataFrame]
    #         A dictionary containing DataFrames of the dimensionless PSE field values.
    #     ID_MACH : int
    #         The ID of the Mach case for retrieving reference values.
    #
    #     Returns
    #     -------
    #     dict[str, pd.DataFrame]
    #         A dictionary of the dimensionalized PSE field values.
    #     """
    #     ref_values = get_reference_values().iloc[ID_MACH - 1]
    #     scaling_factors = {
    #             'ux': ref_values['ux'],
    #             'ur': ref_values['ux'],
    #             'ut': ref_values['ux'],
    #             'p': ref_values['rho'] * (ref_values['ux'] ** 2),
    #             'rho': ref_values['rho']
    #     }
    #
    #     pse_dim = {}
    #     for key in dimless_pse:
    #         for quantity, factor in scaling_factors.items():
    #             if quantity in key:
    #                 pse_dim[key] = dimless_pse[key] / factor
    #                 break
    #
    #     return pse_dim

    def interpolate(self) -> dict[str, pd.DataFrame]:
        """
        Interpolate the RANS values to the PSE grid and update the RANS values directly.

        """
        rans_field = RansField(self.ID_MACH)
        r_grid = get_r_grid()
        rans_interpolated = {}
        for quantity in self.rans_quantities:
            field = np.zeros((len(self.x_grid), len(r_grid)))

            for i, r_val in enumerate(r_grid):
                rans_values_at_r = rans_field.values[quantity].iloc[:, i]

                cs = CubicSpline(rans_field.x, rans_values_at_r)

                field[:, i] = cs(self.x_grid)

            rans_interpolated[quantity] = pd.DataFrame(field)

        return rans_interpolated

    def __get_raw_perturbation_values(self):
        """Retrieve Results from stability fields as a dictionary of DataFrames with integer indexing.

        Returns
        -------
        dict
            A dictionary where each key is a quantity name and the value is a DataFrame
            with integer indices for rows (x-axis) and columns (r-axis).
        """

        dir_st = DIR_STABILITY / "St{:02d}".format(int(10 * self.St))
        if not dir_st.exists():
            raise FileNotFoundError(f"Directory '{dir_st}' does not exist in {DIR_STABILITY}")

        dir_field = dir_st / 'Field'
        file_perturbation = self.__find_file(dir_field)

        full_data = pd.read_csv(
                file_perturbation,
                delimiter=r'\s+',
                skiprows=3,
                names=self.pse_quantities,
        )

        x_values = full_data['x'].unique()
        nx = range(len(x_values))
        nr = range(len(get_r_grid()))
        perturbation_dict = {}

        for quantity in self.pse_quantities[2:]:
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

        dir_st  = DIR_STABILITY / "St{:02d}".format(int(10 * self.St))
        if not dir_st.exists():
            raise FileNotFoundError(f"Directory '{dir_st}' does not exist in {DIR_STABILITY}")

        dir_alpha = dir_st / 'alpha'
        file_alpha = self.__find_file(dir_alpha)


        return pd.read_csv(file_alpha,
                           delimiter=r'\s+',
                           skiprows=3,
                           names=self.stability_quantities).drop(labels=['x', 'C<sub>ph</sub>', 'sigma', 'N'],
                                                                 axis='columns')

    def __find_file(self, directory):
        files = list(directory.glob('*/*'))
        wanted_file = None
        for i, file in enumerate(files):
            if file.stem.endswith(str(self.ID_MACH)):
                wanted_file = files[i]

        if wanted_file is None:
            raise FileNotFoundError('File not found - Case might be available')

        return wanted_file