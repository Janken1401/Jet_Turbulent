from scipy.io import savemat

from Field.perturbation_field import PerturbationField
from src.Field.post_process import PostProcess
from toolbox.path_directories import DIR_OUT

# Instanciation d'un objet PostProcess
postpross_04_001 = PostProcess(0.4, 1, epsilon=0.01, t=0)

# Figure 1
postpross_04_001.plot_field('rans', 'ux', x_max=8, r_max=2)
postpross_04_001.plot_field('rans', 'ur', x_max=8, r_max=2)

# Figure 2
postpross_04_001.plot_field('pse', 'abs(ux)', x_max=8, r_max=2)
postpross_04_001.plot_field('pse', 'abs(ur)', x_max=8, r_max=2)

# Figure 3
postpross_04_001.plot_field('total', 'ux', x_max=8, r_max=2)
postpross_04_001.plot_field('total', 'ur', x_max=8, r_max=2)

# Figure 4
postpross_04_001.plot_line('total', 'ux', [50, 142, 86])
