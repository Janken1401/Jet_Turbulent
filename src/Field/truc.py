import numpy as np
import pandas as pd

from Field.perturbation_field import perturbationField
from src.ReadData.read_radius import get_r_grid

r_grid = get_r_grid()
pert_field = perturbationField(St=0.4, ID_MACH=1)
values = pert_field.get_perturbation_field()