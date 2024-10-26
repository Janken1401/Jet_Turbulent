import numpy as np

R = 287.1 # Gas constant
gamma = 1.4  # Heat Capacity ratio
D = 38 # mm
p_0 = 98_000 # Pa
T_0 = 288.15 # K


rho_0 = p_0 / (R * T_0)
c_0 = np.sqrt(gamma * R * T_0)

T_s = (gamma - 1) * T_0 # Stagnation temperature
