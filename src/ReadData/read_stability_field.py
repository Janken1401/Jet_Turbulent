import numpy as np
import pandas as pd
from src.toolbox.path_directories import DIR_DATA
from src.ReadData.read_info import get_mach_reference
from toolbox.path_directories import DIR_STABILITY

path_mach = DIR_DATA / 'Mach.dat'


class perturbationField:
    def __init__(self, St, ID_MACH):
        if not isinstance(St, (int,float)):
            raise TypeError('St must be a float')
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')
        self.St = St
        self.ID_MACH = ID_MACH
        self.mach = get_mach_reference().loc[self.ID_MACH - 1]
        dir_St = DIR_STABILITY / "St{:02d}".format(int(10 * self.St))
        dir_field = dir_St / f'FrancCase_{self.ID_MACH}'
        self.file_perturbation = dir_field / f'pertpse_FrancCase_{self.ID_MACH}.dat'
        self.stability_field = self._get_stability_field()

    def _get_stability_field(self):
        """Retrieve Results from stability  fields

        Returns
        -------
        DataFrame
            a DataFrame containing all values for all the Mach numbers like
        """

        # Used read_csv instead with space delimiter instead of read_fwf in case
        # of floating inconsistency.
        return pd.read_csv(self.file_perturbation,
                           delimiter=r'\s+',
                           skiprows=3,
                           names=['x', 'r',
                                  'Re(ux)', 'Im(ux)', 'abs(ux)',
                                  'Re(ur)', 'Im(ur)', 'abs(ur)',
                                  'Re(ut)', 'Im(ut)', 'abs(ut)',
                                  'Re(rho)', 'Im(rho)', 'abs(rho)',
                                  'Re(p)', 'Im(p)', 'abs(p)']
                           )
