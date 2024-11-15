from typing import Union

import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy.interpolate import CubicSpline

from src.ReadData.read_radius import get_r_grid
from src.Field.rans_field import RansField
from src.toolbox.path_directories import DIR_STABILITY
from src.ReadData.read_info import get_reference_values
from src.toolbox.dimless_reference_values import D, c_0, p_0, rho_0, gamma


class PerturbationField:
    """
    Class to handle the retrieval, processing, and interpolation of perturbation fields in
    a stability analysis setup. This class computes and interpolates various fields, including
    RANS, PSE, and stability fields, to facilitate stability analysis computations.

    Attributes
    ----------
    rans_quantities : list of str
        Quantities for which RANS field data is available.
    pse_quantities : list of str
        Perturbation field quantities to retrieve, with each represented in real, imaginary, or magnitude forms.
    stability_quantities : list of str
        List of stability field values, such as the real and imaginary parts of alpha and derived quantities.
    x_grid : np.ndarray
        Array of x-coordinates used for grid alignment in interpolation.
    values : dict of str : pd.DataFrame
        Dictionary containing perturbation field values for each quantity across the x- and r-axes.
    St : float
        Strouhal number for frequency-based analysis.
    ID_MACH : int
        Mach number ID representing a specific case setup.

    Methods
    -------
    compute_total_field(t: Union[int, float] = 0, epsilon_q: Union[int, float] = 0.01) -> dict[str, pd.DataFrame]
        Calculates the total field by combining RANS and perturbation fields.

    compute_perturbation_field(t_percent_T: Union[int, float] = 0) -> dict[str, pd.DataFrame]
        Generates the perturbation field by combining real and imaginary parts and applying a time-based multiplier.

    convert_to_rans_reference(dimless_field: dict[str, pd.DataFrame], ID_MACH: int) -> dict[str, pd.DataFrame]
        Converts dimensionless PSE field values to the RANS reference frame.

    interpolate() -> dict[str, pd.DataFrame]
        Interpolates RANS values to align with the PSE grid for consistency.

    __get_raw_perturbation_values() -> None
        Retrieves raw perturbation values from a file and organizes them by quantity and grid indices.

    get_stability_data() ->  pd.DataFrame
        Reads stability data for further stability-based calculations.

    __find_file(directory: Path) -> Path
        Finds the file specific to the Mach ID case within a directory structure.
    """
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

    def __init__(self, St: float, ID_MACH: int) -> None:
        """
         Initializes the PerturbationField with Strouhal number and Mach case ID. Loads necessary
         perturbation and RANS field data.

         Parameters
         ----------
         St : float
             Strouhal number
         ID_MACH : int
            Case selected based on the Mach reference.

         Raises
         ------
         ValueError
             If `St` is not a positive float or `ID_MACH` is not a positive integer.
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
        self.rans_values = RansField.convert_to_pse_ref(self.interpolate(), self.ID_MACH)

    def compute_total_field(self, t: Union[int, float] = 0, epsilon_q: Union[int, float] = 0.01):
        """
        Computes the total field by summing the base RANS field and a scaled perturbation field.

        Parameters
        ----------
        t : int or float, optional
            Percentage of the period (0 to 100) used to compute the perturbation field phase, by default 0.
        epsilon_q : int or float, optional
            Amplitude scaling factor for perturbations, by default 0.01.

        Returns
        -------
        dict[str, pd.DataFrame]
            Dictionary with total field quantities in RANS reference for each field.

        Raises
        ------
        ValueError
            If `t` is not in [0, 100] or if `epsilon_q` is negative.
        """
        if not isinstance(t, (int, float)) or not (0 <= t <= 100):
            raise ValueError("t should be a percentage between 0 and 100.")
        if not isinstance(epsilon_q, (int, float)) or epsilon_q < 0:
            raise ValueError("epsilon_q should be a positive float or integer.")

        q_tot = {}

        q_prime = self.compute_perturbation_field(t_percent_T=t)
        q_prime = self.convert_to_rans_reference(q_prime, self.ID_MACH)
        self.rans_values = self.convert_to_rans_reference(self.rans_values, self.ID_MACH)
        for rans_quantity in self.rans_quantities:
            perturbation = epsilon_q * np.real(q_prime[rans_quantity])
            q_tot[rans_quantity] = self.rans_values[rans_quantity] + perturbation

        return self.convert_to_rans_reference(q_tot, self.ID_MACH)

    def compute_perturbation_field(self, t_percent_T: Union[int, float] = 0) -> dict[str, pd.DataFrame]:
        """
        Computes the time-dependent perturbation field values from real and imaginary parts.

        Parameters
        ----------
        t_percent_T : int or float, optional
            Time as a percentage of the period `T`, by default 0.

        Returns
        -------
        dict[str, pd.DataFrame]
            Perturbation field values as complex values for each quantity.

        Raises
        ------
        ValueError
            If `t_percent_T` is not between 0 and 100.
        """
        if not isinstance(t_percent_T, (int, float)) or not (0 <= t_percent_T <= 100):
            raise ValueError("t_percent_T must be a positive number between 0 and 100.")

        stability_data = self.get_stability_data()
        theta_real = stability_data['Re(int(alpha))']
        theta_imag = stability_data['Im(int(alpha))']

        T = 2 * np.pi / self.St
        t = (t_percent_T / 100) * T

        time_multiplier = np.exp(-theta_imag) * np.exp(1j * (theta_real - (self.St * t)))

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
        Converts a dimensionless PSE field to the RANS reference for nondimensionless values.

        Parameters
        ----------
        dimless_field : dict[str, pd.DataFrame]
            Dimensionless PSE field values for each quantity.
        ID_MACH : int
            Mach case ID for retrieving reference values specific to the case.

        Returns
        -------
        dict[str, pd.DataFrame]
            Converted field values scaled to the RANS reference system.
        """
        conversion_factors = {
                'ux': c_0,
                'ur': c_0,
                'ut': c_0,
                'p': gamma * p_0,
                'rho': rho_0
        }

        ref_values = get_reference_values(ID_MACH)
        scaling_factors = {
                'ux': ref_values['ux'],
                'ur': ref_values['ux'],
                'ut': ref_values['ux'],
                'p': ref_values['rho'] * (ref_values['ux'] ** 2),
                'rho': ref_values['rho']
        }

        pse_to_rans = {}
        for key, df in dimless_field.items():
            for quantity in conversion_factors:
                if quantity in key:
                    conv_factor = conversion_factors[quantity]
                    scale_factor = scaling_factors[quantity]
                    pse_to_rans[key] = df * (scale_factor / conv_factor)
                    break

        return pse_to_rans

    def interpolate(self) -> dict[str, pd.DataFrame]:
        """
        Interpolates RANS field values onto the PSE grid using cubic spline interpolation. The interpolation assumes
        that the r-grid is the same for both grid.
        If it is not the case, please use the scipy.interpolate.griddata.
        For these data, the expected result is that each 5-ith row in the RANS grid must match the i-th row in PSE grid
        Hence , a test case for St = 0.4 and Case 1 has been conducted for ux resulting in a
        Mismatch at x_rans=505, x_pse=101, r_idx=0
        RANS Value: 0.5338967816273286, Interpolated Value: 0.5352458183174091
        which is a 0.001349036690080574 difference

        Returns
        -------
        dict[str, pd.DataFrame]
            Interpolated values of the RANS field aligned with the PSE grid.
        """
        rans_field = RansField(self.ID_MACH)
        r_grid = get_r_grid()
        rans_interpolated = {}
        for quantity in RansField.quantities:
            field = np.zeros((len(self.x_grid), len(r_grid)))

            for i, r_val in enumerate(r_grid):
                rans_values_at_r = rans_field.values[quantity].iloc[:, i]

                cs = CubicSpline(rans_field.x, rans_values_at_r)

                field[:, i] = cs(self.x_grid)

            rans_interpolated[quantity] = pd.DataFrame(field)

        return rans_interpolated

    def __get_raw_perturbation_values(self):
        """
        Retrieves perturbation field data from stored files. Parses and structures data for each quantity
        based on `x` and `r` grid indices.

        Raises
        ------
        FileNotFoundError
            If the directory for the specified Strouhal number case does not exist.
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
        """
        Loads stability field data, containing values such as real and imaginary parts of `alpha`.

        Returns
        -------
        DataFrame
            DataFrame containing stability analysis results.

        Raises
        ------
        FileNotFoundError
            If the directory or specific file for stability data is not found.
        """

        dir_st = DIR_STABILITY / "St{:02d}".format(int(10 * self.St))
        if not dir_st.exists():
            raise FileNotFoundError(f"Directory '{dir_st}' does not exist in {DIR_STABILITY}")

        dir_alpha = dir_st / 'alpha'
        file_alpha = self.__find_file(dir_alpha)

        return pd.read_csv(file_alpha,
                           delimiter=r'\s+',
                           skiprows=3,
                           names=self.stability_quantities)

    def __find_file(self, directory):
        """
       Locates a file associated with the specified Mach case ID within a given directory.

       Parameters
       ----------
       directory : Path
           Directory where files are searched for the Mach case ID.

       Returns
       -------
       Path
           Path to the file corresponding to the selected Mach case.

       Raises
       ------
       FileNotFoundError
           If no file for the specified Mach case is found within the directory.
       """
        files = list(directory.glob('*/*'))
        wanted_file = None
        for i, file in enumerate(files):
            if file.stem.endswith(str(self.ID_MACH)):
                wanted_file = files[i]

        if wanted_file is None:
            raise FileNotFoundError('File not found - Case might be available')

        return wanted_file
