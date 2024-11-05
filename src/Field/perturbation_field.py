import pandas as pd
from matplotlib import ticker
from pandas import DataFrame
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

from ReadData.read_radius import get_r_grid
from src.Field.rans_field import RansField
from src.toolbox.path_directories import DIR_STABILITY
from src.ReadData.read_info import get_reference_values
from src.toolbox.dimless_reference_values import *


class PerturbationField:
    pse_value_names = ['x', 'r',
                       'Re(ux)', 'Im(ux)', 'abs(ux)',
                       'Re(ur)', 'Im(ur)', 'abs(ur)',
                       'Re(ut)', 'Im(ut)', 'abs(ut)',
                       'Re(rho)', 'Im(rho)', 'abs(rho)',
                       'Re(p)', 'Im(p)', 'abs(p)']

    def __init__(self, St=0.4, ID_MACH=1):
        """

        Parameters
        ----------
        St: int or float
            Strouhal Number
        ID_MACH: int
            Case selected
        """
        self.values = None
        self.r_grid = get_r_grid()
        if not isinstance(St, (int, float)):
            raise TypeError('St must be a float')
        if not isinstance(ID_MACH, int):
            raise TypeError('ID_MACH must be a int')
        self.St = St
        self.ID_MACH = ID_MACH
        self.rans_field = RansField(self.ID_MACH)
        self.get_perturbation_values()
        self.rans_field.interpolate(self.x_grid)
        self.rans_values = self.rans_field.interpolated_values

    def convert_to_rans_reference(self):
        """
        Set the dimensionized RANS into the PSE reference system

        Returns
        -------
        rans_pse: dict
            contains DataFrame of the rans field in PSE reference system
        """

        pse_dim = self.pse_dimensionalized()
        pse_to_rans = {
                'abs(ux)': pse_dim['abs(ux)'] / c_0,
                'Re(ux)': pse_dim['Re(ux)'] / c_0,
                'Im(ux)': pse_dim['Im(ux)'] / c_0,
                'abs(ur)': pse_dim['abs(ur)'] / c_0,
                'Re(ur)': pse_dim['Re(ur)'] / c_0,
                'Im(ur)': pse_dim['Im(ur)'] / c_0,
                'abs(rho)': pse_dim['abs(rho)'] / c_0,
                'Re(rho)': pse_dim['Re(rho)'] / c_0,
                'Im(rho)': pse_dim['Im(rho)'] / rho_0,
                'abs(p)': pse_dim['abs(p)'] / (gamma * p_0),
                'Re(p)': pse_dim['Re(p)'] / (gamma * p_0),
                'Im(p)': pse_dim['Im(p)'] / (gamma * p_0),
        }

        return pse_to_rans

    def pse_dimensionalized(self):
        """
        Re-dimensionalize the RANS field before set it to the PSE reference

        Returns
        -------
        rans_dim : dict
            contains DataFrame of the rans field except for x and r
        """
        ref_values = get_reference_values().iloc[self.ID_MACH - 1]
        pse_dim = {
                'abs(ux)': self.values['abs(ux)'] * ref_values['ux'],
                'Re(ux)': self.values['Re(ux)'] * ref_values['ux'],
                'Im(ux)': self.values['Im(ux)'] * ref_values['ux'],
                'abs(ur)': self.values['abs(ur)'] * ref_values['ux'],
                'Re(ur)': self.values['Re(ur)'] * ref_values['ux'],
                'Im(ur)': self.values['Im(ur)'] * ref_values['ux'],
                'abs(p)': self.values['abs(p)'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'Re(p)': self.values['Re(p)'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'Im(p)': self.values['Im(p)'] * ref_values['rho'] * ref_values['ux'] ** 2,
                'abs(rho)': self.values['abs(rho)'] * ref_values['rho'],
                'Re(rho)': self.values['Re(rho)'] * ref_values['rho'],
                'Im(rho)': self.values['Im(rho)'] * ref_values['rho']
        }

        return pse_dim

    def get_interpolated_values(self, x_grid):
        return self.rans_field.interpolate(x_grid=x_grid)

    def get_perturbation_values(self):
        """Retrieve Results from stability fields as a dictionary of DataFrames with integer indexing.

        Returns
        -------
        dict
            A dictionary where each key is a quantity name and the value is a DataFrame
            with integer indices for rows (x-axis) and columns (r-axis).
        """

        # Load the perturbation data
        dir_St = DIR_STABILITY / f"St{int(10 * self.St):02d}"
        dir_field = dir_St / 'Field' / f'FrancCase_{self.ID_MACH}'
        file_perturbation = dir_field / f'pertpse_FrancCase_{self.ID_MACH}.dat'

        # Read the full data into a DataFrame
        full_data = pd.read_csv(
                file_perturbation,
                delimiter=r'\s+',
                skiprows=3,
                names=self.pse_value_names
        )

        # Extract the unique `x` and `r` values for indexing
        x_values = full_data['x'].unique()

        # Initialize dictionary to hold each quantity as a DataFrame
        perturbation_dict = {}

        # For each quantity (excluding 'x' and 'r'), pivot into a DataFrame
        for quantity in self.pse_value_names[2:]:
            # Pivot and reset index and columns to integers
            quantity_df = full_data.pivot(index='x', columns='r', values=quantity)
            quantity_df.index = range(len(quantity_df))  # Reset row indices to 0, 1, ..., Nx-1
            quantity_df.columns = range(len(quantity_df.columns))  # Reset column indices to 0, 1, ..., Nr-1
            perturbation_dict[quantity] = quantity_df

        # Save the dictionary and index arrays to instance attributes
        self.values = perturbation_dict
        self.x_grid = x_values
