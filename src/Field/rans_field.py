import pandas as pd
from scipy.io import loadmat

from toolbox.path_directories import DIR_MEAN, RANS_FILES
from toolbox.dimless_reference_values import gamma, rho_0, c_0, T_0, p_0


class RansField:

    quantities = ['rho', 'ux', 'ur', 'ut', 'p', 'T']

    def __init__(self, ID_MACH):
        """
        Parameters
        ----------
        ID_MACH : int
            ID of the Mach reference
        """
        self.values = None
        self.x = None
        if not isinstance(ID_MACH, int) and ID_MACH <= 0:
            raise TypeError('ID_MACH must be a positive integer')

        self.ID_MACH = ID_MACH
        self.__get_rans_values()

    @staticmethod
    def dimensionalized(dimless_field: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Re-dimensionalize the RANS field based on PSE reference values.

        Parameters
        ----------
        dimless_field : dict
            Dictionary containing dimensionless values for each field quantity.

        Returns
        -------
        dict
            Dictionary of DataFrames with dimensionalized RANS field values, except for 'x' and 'r'.
        """
        # Define conversion factors for each field, skipping x and r
        conversion_factors = {
                'ux': c_0,
                'ur': c_0,
                'ut': c_0,
                'T': (gamma - 1) * T_0,
                'p': gamma * p_0,
                'rho': rho_0
        }

        rans_dim = {}

        for field, factor in conversion_factors.items():
            if field in dimless_field:
                rans_dim[field] = dimless_field[field] * factor
            else:
                print(f"Warning: '{field}' is missing in dimless_field, skipping dimensionalization.")

        return rans_dim

    def __get_rans_values(self) -> None:
        """
        Retrieve values of the RANS mean field based on the mach case selected

        Returns
        -------
        Dict: a dict containing DataFrame for each value computed in the RANS field
        """
        rans_quantities = ['rho', 'ux', 'ur', 'ut', 'T', 'p']

        rans_file = DIR_MEAN / RANS_FILES[self.ID_MACH]
        if rans_file.exists():
            rans_field_array = loadmat(rans_file)['arr']
        else:
            raise ValueError('mat file not found - The case you have entered might not be available')

        nx, nr, nvalues = rans_field_array.shape  # 536, 69, 8
        self.x = rans_field_array[:, 0, 0]
        self.values = {name: pd.DataFrame(rans_field_array[:, :, i + 2], index=range(nx), columns=range(nr))
                       for i, name in enumerate(rans_quantities)}
