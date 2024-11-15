import pandas as pd
from scipy.io import loadmat

from ReadData.read_info import get_reference_values
from toolbox.path_directories import CASE_NUMBER, DIR_MEAN, RANS_FILES
from toolbox.dimless_reference_values import gamma, rho_0, c_0, T_0, p_0


class RansField:
    """
    Class for handling and dimensionalizing the RANS (Reynolds-Averaged Navier-Stokes) mean field data for various quantities.
    This class provides methods to retrieve, store, and convert RANS field data to dimensional values for specific Mach cases.

    Attributes
    ----------
    quantities : list of str
        List of available RANS quantities (e.g., 'rho', 'ux', 'ur', 'ut', 'T', 'p') in the data file.
    ID_MACH : int
        Identifier for the Mach case to load the correct data file.
    values : dict of str : pd.DataFrame
        Dictionary where each key is a quantity name and each value is a DataFrame of RANS field data.
    x : np.ndarray
        Array of x-coordinates used in the RANS field data for spatial referencing.

    Methods
    -------
    dimensionalized(dimless_field: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]
        Converts a dictionary of dimensionless field data into dimensional quantities based on reference values.
    convert_to_pse_ref(dimless_field: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]
        Converts a dictionary of dimensionless field data into dimensionless values in the stability reference.
    __get_rans_values() -> None
        Loads RANS field values from a .mat file and stores them as DataFrames, using the ID_MACH attribute for file selection.
    """

    quantities = ['rho', 'ux', 'ur', 'ut', 'T', 'p']

    def __init__(self, ID_MACH):
        """
        Initializes the RansField class by setting the Mach case ID and loading RANS field values.

        Parameters
        ----------
        ID_MACH : int
            Identifier for the Mach case to select the appropriate RANS data file.

        Raises
        ------
        TypeError
            If `ID_MACH` is not a positive integer.
        """
        self.values = None
        self.x = None
        if not isinstance(ID_MACH, int) or ID_MACH <= 0 or ID_MACH > CASE_NUMBER:
            raise TypeError(f'ID_MACH must be a positive integer comprised between 0 and {CASE_NUMBER}')

        self.ID_MACH = ID_MACH
        self.__get_rans_values()

    @staticmethod
    def convert_to_pse_ref(dimless_field: dict[str, pd.DataFrame], ID_MACH: int) -> dict[str, pd.DataFrame]:
        """
        Converts dimensionless RANS field values to the stability reference.

        Parameters
        ----------
        dimless_field : dict of str : pd.DataFrame
            Dictionary where each key is a field name (e.g., 'ux', 'T') and each value is a DataFrame of dimensionless field values.

        Returns
        -------
        dict of str : pd.DataFrame
            Dictionary with dimensionless RANS field values in the stability reference for each field except 'x' and 'r'.

        Notes
        -----
        The method applies different conversion factors to each field:
        - 'ux', 'ur', 'ut' are scaled by the speed of sound `c_0`.
        - 'T' is scaled by a factor based on the adiabatic constant `gamma` and reference temperature `T_0`.
        - 'p' is scaled by a factor involving `gamma` and reference pressure `p_0`.
        - 'rho' is scaled by the reference density `rho_0`.

        Warnings
        --------
        If a field in `quantities` is missing from `dimless_field`, a warning is printed and it is skipped.
        """

        ref_values = get_reference_values(ID_MACH)
        scaling_factors = {
            'ux': ref_values['ux'],
            'ur': ref_values['ux'],
            'ut': ref_values['ux'],
            'p': ref_values['rho'] * (ref_values['ux'] ** 2),
            'rho': ref_values['rho']
        }
        dim_field = RansField.dimensionalized(dimless_field)
        rans_pse = {}

        for field, scale in scaling_factors.items():
            if field in dim_field:
                rans_pse[field] = dim_field[field] / scale
            else:
                print(f"Warning: '{field}' is missing in dimless_field, skipping dimensionalization.")

        return rans_pse

    @staticmethod
    def dimensionalized(dimless_field: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Converts dimensionless RANS field values to dimensional values based on known reference values.

        Parameters
        ----------
        dimless_field : dict of str : pd.DataFrame
            Dictionary where each key is a field name (e.g., 'ux', 'T') and each value is a DataFrame of dimensionless field values.

        Returns
        -------
        dict of str : pd.DataFrame
            Dictionary with dimensionalized RANS field values for each field except 'x' and 'r'.

        Notes
        -----
        The method applies different conversion factors to each field:
        - 'ux', 'ur', 'ut' are scaled by the speed of sound `c_0`.
        - 'T' is scaled by a factor based on the adiabatic constant `gamma` and reference temperature `T_0`.
        - 'p' is scaled by a factor involving `gamma` and reference pressure `p_0`.
        - 'rho' is scaled by the reference density `rho_0`.

        Warnings
        --------
        If a field in `quantities` is missing from `dimless_field`, a warning is printed and it is skipped.
        """
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
        Loads the RANS field data from a .mat file for the specified Mach case ID.
        The loaded data is stored in the `values` attribute as a dictionary where each field
        quantity (e.g., 'ux', 'rho') is represented by a DataFrame with `x` and `r` as indices.

        Raises
        ------
        ValueError
            If the specified .mat file does not exist for the given Mach case ID.

        Notes
        -----
        The .mat file must contain an array `arr` with a shape `(nx, nr, nvalues)`. The first two
        columns of `arr` are assumed to be the `x` and `r` coordinates, and the remaining columns
        correspond to the field quantities specified in `quantities`.
        """

        rans_file = DIR_MEAN / RANS_FILES[self.ID_MACH]
        if rans_file.exists():
            rans_field_array = loadmat(rans_file)['arr']
        else:
            raise ValueError('mat file not found - The case you have entered might not be available')

        nx, nr, nvalues = rans_field_array.shape  # 536, 69, 8
        self.x = rans_field_array[:, 0, 0]
        self.values = {name: pd.DataFrame(rans_field_array[:, :, i + 2], index=range(nx), columns=range(nr))
                       for i, name in enumerate(self.quantities)}
