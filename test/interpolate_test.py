import unittest

from Field.rans_field import RansField
from ReadData.read_radius import get_r_grid
from src.Field.perturbation_field import PerturbationField

class TestRANSInterpolation(unittest.TestCase):

    def setUp(self):
        self.pert_field = PerturbationField(0.4, 1)
        self.rans_field = RansField(1)

    def test_interpolation(self):
        for pse_idx in [1, 101, 200]:
            rans_idx = 5 * pse_idx

            for r_idx in range(len(get_r_grid())):
                rans_val = self.rans_field.values['ux'].iloc[rans_idx, r_idx]
                interp_val = self.pert_field.rans_values['ux'].iloc[pse_idx, r_idx]

                try:
                    self.assertAlmostEqual(rans_val, interp_val, places=5)
                except AssertionError as e:
                    print(f"Mismatch at x_rans={rans_idx}, x_pse={pse_idx}, r_idx={r_idx}")
                    print(f"RANS Value: {rans_val}, Interpolated Value: {interp_val}")
                    raise e
if __name__ == '__main__':
    unittest.main()