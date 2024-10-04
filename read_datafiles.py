from os.path import dirname, join as pjoin
from scipy.io import loadmat

data_dir = pjoin('Data', 'MeanFlow')
mat_fname = pjoin(data_dir, 'mean_1.mat')

mat_contents = loadmat(mat_fname)
truc = mat_contents['arr']
print(truc)