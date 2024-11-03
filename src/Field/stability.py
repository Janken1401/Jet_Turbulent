import pandas as pd
from matplotlib import pyplot as plt

from toolbox.fig_parameters import RANS_FIGSIZE
from toolbox.path_directories import DIR_STABILITY


class Stability:
    def __init__(self, St, ID_MACH):
        """
        Parameters
        ----------
        St: int or float
            Strouhal Number
        ID_MACH: int
            Case selected
        """
        if not isinstance(St, (int, float)):
            raise TypeError('St must be a float or an int')
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')
        self.St = St
        self.ID_MACH = ID_MACH
        self.stability_value = self.get_stability_data()


    def get_stability_data(self):
        """Retrieve Results from stability fields

        Returns
        -------
        DataFrame
            a DataFrame containing all values from the perturbation field results
        """

        # Used read_csv instead with space delimiter instead of read_fwf in case
        # of floating inconsistency.
        dir_St = DIR_STABILITY / "St{:02d}".format(int(10 * self.St))
        dir_field = dir_St / 'alpha' / f'FrancCase_{self.ID_MACH}'
        file_stability = dir_field / f'vappse_FrancCase_{self.ID_MACH}.dat'

        return pd.read_csv(file_stability,
                           delimiter=r'\s+',
                           skiprows=3,
                           names=['x',
                                  'Re(alpha)', 'Im(alpha)', 'abs(alpha)',
                                  'Re(int(alpha))', 'Im(int(alpha))',
                                  'C<sub>ph</sub>', 'sigma', 'N']).drop(labels=['C<sub>ph</sub>', 'sigma', 'N'], axis='columns')


