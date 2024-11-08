import pandas as pd
from scipy.io import loadmat

from ReadData.read_info import get_reference_values
from src.toolbox.path_directories import DIR_MEAN, RANS_FILES
from src.toolbox.dimless_reference_values import gamma, rho_0, c_0, T_0, p_0


class RansField:

    def __init__(self, ID_MACH=1):
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
    def dimensionalized(dimless_field):
        """
        Re-dimensionalize the RANS field before set it to the PSE reference

        Returns
        -------
        rans_dim : dict
            contains DataFrame of the rans field except for x and r
        """
        rans_dim = {
                'ux': dimless_field['ux'] * c_0,
                'ur': dimless_field['ur'] * c_0,
                'ut': dimless_field['ut'] * c_0,
                'T': dimless_field['T'] * (gamma - 1) * T_0,
                'p': dimless_field['p'] * gamma * p_0,
                'rho': dimless_field['rho'] * rho_0
        }

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
