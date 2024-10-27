import numpy as np

R = 287.1 # Gas constant
gamma = 1.4  # Heat Capacity ratio
D = 38e-1 # mm
p_ref = 98_000 # Pa
T_ref = 288.15 # K

rho_0 = p_ref / (R * T_ref)
c_ref = np.sqrt(gamma * R * T_ref)

T_s = (gamma - 1) * T_ref # Stagnation temperature