import numpy as np

def set_data_from_file(filename, unpack=False, skiprows=1, vb=True):
    """
    get all the data field
    :param filename: file with data
    :param skiprows: integer, to not read the first commented lines
    :param unpack: boolean, date in n x m or m x n matrices
    :param vb: verbose, boolean if True display the matrice shape
    # be careful with unpack, check at each time,
    """
    with open(filename, "r") as infile:
        data = np.loadtxt(infile, dtype=float, unpack=unpack, skiprows=skiprows)
        if vb:
            print("file name   : ", filename)
            print("data shape  : ", data.shape)
        return data

def load_data(filename, skiprows=2, vb=True):
    """
    load all the data simultaenously
    :param filename: a list of string
    :param vb: boolean, verbose to display the data shape
    :param skiprows: integer, number of line to no read at the beginning of the files
    :return data: a numpy array with the data
    """
    data = []
    for file in filename:
        data.append(set_data_from_file(file, skiprows=skiprows, vb=vb))
    return data