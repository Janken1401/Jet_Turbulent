import numpy as np
import pandas as pd
from src.toolbox.path_directories import DIR_DATA
from src.toolbox.dimless_reference_values import gamma, R
from toolbox.path_directories import DIR_STABILITY

path_perturbation = DIR_STABILITY_FIELD / 'FrancCase_1' / 'pertpse_FrancCase_1.dat'
path_mach = DIR_DATA / 'Mach.dat'


class perturbationField:
    def __init__(self, St, ID_MACH):
        self.St = St
        self.ID_MACH = ID_MACH
        dir_St = DIR_STABILITY / "St{:02d}".format(int(10*self.St))
        dir_field = dir_St / f'FrancCase_{self.ID_MACH}
        field_file = dir_field / f'pertpse_FrancCase_{self.ID_MACH}.dat'







    # def stability_field_values():
    #     """Retrieve Results from stability  fields
    #
    #     Returns
    #     -------
    #     DataFrame
    #         a DataFrame containing all values for all the Mach numbers like
    #     """
    #
    #     # Used read_csv instead with space delimiter instead of read_fwf in case
    #     # of floating inconsistency.
    #     return pd.read_csv(path_perturbation,
    #                        delimiter=r'\s+',
    #                        skiprows=3,
    #                        names=['x', 'r',
    #                               'Re(ux)', 'Im(ux)', 'abs(ux)',
    #                               'Re(ur)', 'Im(ur)', 'abs(ur)',
    #                               'Re(ut)', 'Im(ut)', 'abs(ut)',
    #                               'Re(rho)', 'Im(rho)', 'abs(rho)',
    #                               'Re(p)', 'Im(p)', 'abs(p)']
    #                        )

