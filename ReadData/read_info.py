import pandas as pd

from toolbox.constantes import __DIR__

path = __DIR__ + "info.dat"

info = pd.read_csv(path, delimiter=r'\s+', comment='#',names=["ux", "rho",
                                                              "T", "P"])

print(info.ux)