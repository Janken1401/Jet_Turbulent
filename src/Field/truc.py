import pandas as pd
from scipy.io import loadmat

from src.Field.perturbation_field import PerturbationField

pert_field = PerturbationField()





# pivoted = data.pivot(index='x', columns='r', values=pse_value_names).drop(['x', 'r'], axis=1)


names = ['x', 'r', 'rho', 'ux', 'ur', 'ut', 'T', 'P']
rans_file = DIR_MEAN / RANS_FILES[1]
rans_field_array = loadmat(rans_file)['arr']
Nx, Nr, Nvalues = rans_field_array.shape  # 536, 69, 8
x = pd.DataFrame(rans_field_array[:, :, 0])
r = pd.DataFrame(rans_field_array[:, :, 1])
rans = {name: pd.DataFrame(rans_field_array[:, :, i], index=range(Nx), columns=range(Nr))
        for i, name in enumerate(names)}



