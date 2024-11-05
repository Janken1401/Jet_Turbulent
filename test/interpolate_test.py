import unittest
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

from ReadData.read_radius import get_r_grid
from src.Field.perturbation_field import PerturbationField  # Assuming this is the class for RANS data

class TestRANSInterpolation(unittest.TestCase):

    def setUp(self):
        # Setup the RANS field with sample data
        self.pert_field = PerturbationField()
        self.rans_field = self.pert_field.rans_field

    # def test_interpolation_matches_at_pse_grid(self):
    #     # Perform interpolation on the PSE grid
    #     self.rans_field.interpolate(self.pert_field.x_grid)
    #     ux_interp = self.rans_field.interpolated_values['ux']
    #
    #     # Define a tolerance for checking equality
    #     tolerance = 0.1
    #
    #     # Test every 5th value in x_pse_grid against original RANS values in x_rans
    #     for i, x_rans_val in enumerate(self.rans_field.x):
    #         if i % 5 == 0:
    #             # Compare the interpolated ux values at this x_pse_val with RANS values
    #             for r_idx, r_val in enumerate(self.rans_field.r):
    #                 rans_ux_value = self.rans_field.values['ux'].iloc[i, r_idx]
    #                 interp_ux_value = ux_interp.iloc[i // 5, r_idx]
    #
    #                 # Assert that interpolated values match RANS values within tolerance
    #                 self.assertAlmostEqual(interp_ux_value, rans_ux_value, delta=tolerance,
    #                                        msg=f"Mismatch at x_rans={i}, x_pse={i//5}")

    def test_interpolation(self):
        # Assuming `rans_field` is the RANS field object, and `pert_field` the PSE field.
        self.rans_field.interpolate(self.pert_field.x_grid)  # Interpolate onto PSE grid

        # Loop through a subset to validate (can refine to more specific key indices if needed)
        for pse_idx in [1, 101, 200]:  # Examples, adjust indices as necessary
            rans_idx = 5 * pse_idx

            for r_idx in range(len(get_r_grid())):  # Loop through each radial index
                rans_val = self.rans_field.values['ux'].iloc[rans_idx, r_idx]
                interp_val = self.rans_field.interpolated_values['ux'].iloc[pse_idx, r_idx]

                # Diagnostic: print if there’s a mismatch
                try:
                    self.assertAlmostEqual(rans_val, interp_val, places=5)
                except AssertionError as e:
                    print(f"Mismatch at x_rans={rans_idx}, x_pse={pse_idx}, r_idx={r_idx}")
                    print(f"RANS Value: {rans_val}, Interpolated Value: {interp_val}")
                    raise e
if __name__ == '__main__':
    unittest.main()