from scipy.io import loadmat

from src.toolbox.path_directories import DIR_MEAN

def get_mean_field_rans(id_mach):
    """

    Parameters
    ----------
    id_mach
        the index of the Mach number referenced in the Mach.dat

    Returns
    -------


    """

    mean_files = DIR_MEAN.glob('*.mat')

    # Sort files by extracting the numeric part of the filename
    sorted_mean_files = sorted(mean_files, key=lambda file: int(file.stem.split('_')[-1]))

    # Return a dictionary with {i: mean_i.mat} structure
    return sorted_mean_files[id_mach - 1]


mean_file = loadmat(DIR_MEAN / 'mean_1.mat')
mean_field = mean_file['arr']






