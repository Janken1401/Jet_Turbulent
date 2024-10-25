from os.path import dirname, join as pjoin
from scipy.io import loadmat
import numpy as np

data_dir = pjoin('../Data', 'MeanFlow')
def get_mean_field_rans(file):
    mat_fname = pjoin(data_dir, 'mean_1.mat')

    mat_contents = loadmat(mat_fname)

    header = mat_contents['__version__']

    truc = mat_contents['arr']
    print(truc.shape)

    print(truc[-1][-1])

