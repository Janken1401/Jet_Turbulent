import numpy as np
import pandas as pd
import scipy
from matplotlib import pyplot as plt, ticker
from typing import Union, Optional

from src.Field.perturbation_field import PerturbationField
from src.Field.rans_field import RansField
from src.ReadData.read_info import get_reference_values
from src.ReadData.read_mach import get_mach_reference
from src.ReadData.read_radius import get_r_grid
from src.toolbox.fig_parameters import RANS_FIGSIZE
from toolbox.fig_parameters import DEFAULT_FIGSIZE
from toolbox.path_directories import DIR_OUT


class PostProcess:
    """
    Class for post-processing and analyzing simulation results from a variety of fields, such as RANS, perturbation, and stability data.
    The class allows for the extraction and visualisation of relevant quantities.

    Attributes
    ----------
    rans_field : RansField
        An instance of the `RansField` class containing the Reynolds-Averaged Navier-Stokes (RANS) field data for a specific Mach case.
    perturbation_field : PerturbationField
        An instance of the `PerturbationField` class containing perturbation data based on a Strouhal number and Mach case.
    ID_MACH : int
        The identifier for the Mach number case used to retrieve relevant data.
    St : float
        The Strouhal number used for perturbation analysis.
    t : float
        A percentage (from 0 to 100) representing a point in the time period `T` for perturbation field evaluation.
    epsilon : float
        A scaling factor applied to perturbation fields when computing the total field.
    x_grid : np.ndarray
        The spatial grid of x-coordinates (e.g., axial or horizontal positions) for the simulation.

    Methods
    -------
    __init__(ID_MACH: int, St: float, t_percent_T: float = 0, epsilon_q: float = 0.01)
        Initializes the PostProcess object by setting the Mach case ID, Strouhal number, time percentage, and
        the amplitude factor.

    compute_total_field()
        Computes the total field by combining the RANS field and the perturbation field, scaled by a factor (`epsilon_q`).

    compute_perturbation_field(t_percent_T: float = 0)
        Computes the perturbation field at a specific point in time (given by `t_percent_T`) using the stability data
        and perturbation values.

    interpolate_rans_field()
        Interpolates the RANS field onto a common grid if the input grid differs from the RANS field's native grid.

    convert_to_dimensionless(rans_field: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]
        Converts the RANS field data from dimensional to dimensionless values, based on reference values for Mach, temperature, etc.

    plot_stability_analysis()
        Generates plots based on stability data, such as growth rates and phase speeds, to analyze the stability of the flow.

    __validate_inputs()
        Validates the user input values (e.g., `t_percent_T`, `epsilon_q`) to ensure they are within acceptable ranges.

    __get_field()
        Retrieves the field values for a specified quantity and field type.

    __get_index()
        Returns the indices corresponding to the specified spatial domain (x and r) based on user input.

    __verbose()
        Prints a summary of the current post-processing object, including relevant parameters like Mach case, Strouhal number, and reference values.

    get_fields_stats(quantity: Optional[str] = None, axis: int = 0) -> Union[pd.DataFrame, dict[str, pd.DataFrame]]
        Retrieves statistical values (mean, standard deviation, variance) for each field along the specified axis (x or r).

    plot_alpha()
        Displays the real and imaginary parts of the growth rate (alpha) for stability analysis.

    plot_field(field: str, name_value: str, x_min: Union[int, float] = 0, x_max: Union[int, float] = 10,
               r_min: Union[int, float] = 0, r_max: Union[int, float] = 5)
        Plots a filled contour of the specified field quantity in a subfield (ranging in x and r).

    plot_line(name_value: str, field: str, x_idx: int)
        Plots a line of a specific quantity at a given x-index for a selected field.

    get_value_in_field(value, x_min=0, x_max=10, r_min=0, r_max=3)
        Returns the specified field values within the desired x and r domain.

    __get_title(field: str, name_value: str) -> str
        Generates the title for a given field and quantity name for plotting purposes.

    __test_validity_input_field(x_min, x_max, r_min, r_max)
        Validates the user input values for plotting, ensuring that the x and r ranges are within the correct domain.

    __get_field(name_value, field)
        Returns the specific field data based on the field type (total, rans, or pse) and the quantity name.

    __get_index(x_min, x_max, r_min, r_max)
        Returns the indices of the x and r grid based on the specified domain.

    __verbose()
        Prints the reference values, Strouhal number, and Mach case if verbosity is enabled.

    Notes
    -----
    - The class combines results from both steady RANS simulations and time-dependent perturbation simulations.
    - It includes functions for both numerical and visual analysis of the data (such as plotting stability growth rates).
    """

    def __init__(self, St: Union[int, float], ID_MACH: int, t: Union[int, float] = 0, epsilon: Union[int, float] = 0.01,
                 verbose: bool = False) -> None:
        """
        Parameters
        ----------
        St: int or float
            Strouhal Number
        ID_MACH: int
            Case selected based on the Mach reference.
        t: int or float - optional
            Dimensionless time, in percentage of the period T = 2pi / St.
        epsilon: int or float - optional
            Amplitude parameter for instabilities.
        verbose: bool
            If True, print reference values and Mach number.
        """
        if not isinstance(St, (int, float)) or St <= 0:
            raise ValueError("St must be a positive float or integer")
        if not isinstance(ID_MACH, int) or ID_MACH <= 0:
            raise ValueError("ID_MACH must be a positive integer")

        self.verbose = verbose
        self.St = St
        self.ID_MACH = ID_MACH
        self.epsilon = epsilon
        self.t = t
        self.perturbation_field = PerturbationField(St, ID_MACH)
        self.x_grid = self.perturbation_field.x_grid
        self.r_grid = get_r_grid()

        if verbose:
            self.__verbose()

    def get_fields_stats(self, quantity: Optional[str] = None, axis: int = 0) -> Union[
        pd.DataFrame, dict[str, pd.DataFrame]]:
        """
         Retrieve the statistical values (mean, standard deviation, ...) for each field along the x-axis (by default)
         or the r-axis.

         Parameters
         ----------
         quantity: str, optional
             The field quantity to retrieve statistics for. If None, statistics for all quantities are returned.
         axis: int, optional
             Axis along which to compute statistics. 0 for x-axis, 1 for r-axis.

         Returns
         -------
         pd.DataFrame or dict[str, pd.DataFrame]
             Statistical values of the field quantity.
         """
        if quantity is not None and not isinstance(quantity, str):
            raise TypeError("quantity must be a string")

        if quantity and quantity not in RansField.quantities:
            raise ValueError(f"{quantity} is not a valid quantity - choose among {RansField.quantities}")

        if axis not in (0, 1):
            raise ValueError("Axis must be 0 or 1")

        stats_dict = {}
        rans_values = self.perturbation_field.rans_values
        if quantity:
            return pd.DataFrame(rans_values[quantity].describe())
        else:
            for quantity in PerturbationField.rans_quantities:
                stats = rans_values[quantity].describe()
                stats_dict[quantity] = stats

        return stats_dict

    def plot_alpha(self):
        """
        Display the values of alpha according to x, showing the real and imaginary parts of the growth rate.

        This function creates two subplots: one for the real part (Re(alpha)) and one for the imaginary part (Im(alpha)).
        """
        stability_data = self.perturbation_field.get_stability_data()
        fig, (ax0, ax1) = plt.subplots(2, 1, figsize=DEFAULT_FIGSIZE, sharex=True)
        ax0.plot(self.x_grid, stability_data["Re(alpha)"], title=r"$\alpha_r$")
        ax1.plot(self.x_grid, stability_data["Im(alpha)"], title=r"$\alpha_i$")
        ax0.get_legend().remove()
        ax1.get_legend().remove()
        fig.tight_layout()
        plt.show()

    def plot_field(self, field: str, name_value: str, x_min: Union[int, float] = 0, x_max: Union[int, float] = 10,
                   r_min: Union[int, float] = 0, r_max: Union[int, float] = 5):
        """
        Plot the contour line (filled) of the desired quantity in a subfield.

        Parameters
        ----------
        field: str
            Field type to plot ('rans', 'pse', or 'total').
        name_value: str
            The specific quantity to plot within the field.
        x_min: int or float, optional
            Minimum value of x for the plot. Default is 0.
        x_max: int or float, optional
            Maximum value of x for the plot. Default is 10.
        r_min: int or float, optional
            Minimum value of r for the plot. Default is 0.
        r_max: int or float, optional
            Maximum value of r for the plot. Default is 5.
        """
        if field not in ["rans", "pse", "total"]:
            raise ValueError("field must be a string in ['rans', 'pse', 'total']")

        self.__test_validity_input_field(x_min, x_max, r_min, r_max)
        value = self.__get_field(name_value, field)

        x, r, value_sub = self.get_value_in_field(value, x_min=x_min, x_max=x_max, r_min=r_min, r_max=r_max)
        plt.style.use("ggplot")
        fig, ax = plt.subplots(figsize=RANS_FIGSIZE, layout="constrained")

        cs = ax.contourf(x, r, value_sub.transpose(), levels=100, cmap="jet")

        plt.xlabel("x/D")
        plt.ylabel("r/D")
        tick_spacing = 1
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax.set_title(self.__get_title(field, name_value))
        cbar = fig.colorbar(cs)
        tick_locator = ticker.MaxNLocator(nbins=5)
        cbar.locator = tick_locator
        cbar.set_ticks(ticks=tick_locator, vmin=value.min(), vmax=value.max())
        cbar.update_ticks()
        plt.show()

    def plot_line(self, field: str, name_value: str, x_idxs: [int, list[int]]):
        """
        Plot the line of a specific quantity at a given x index.

        Parameters
        ----------
        field: str
            Field type to plot ('rans', 'pse', or 'total').
        name_value: str
            The specific quantity to plot within the field.
        x_idx: int or list[int]
            The index of the x-coordinate at which to plot the field data.
        """

        if field not in ["rans", "pse", "total"]:
            raise ValueError("field must be a string in ['rans', 'pse', 'total']")

        if isinstance(x_idxs, int):
            x_idxs = [x_idxs]
        plt.style.use("ggplot")

        fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE, layout="constrained")

        for x_idx in x_idxs:

            if not isinstance(x_idx, int) or not (0 <= x_idx < len(self.x_grid)):
                raise TypeError(f"x_idx must be an integer in [0, {len(self.x_grid) - 1}]")

            value = self.__get_field(name_value, field)
            ax.plot(self.r_grid, value.iloc[x_idx, :],
                    label=rf"$x_{{{x_idx}}} = {self.x_grid[x_idx]}$", linestyle='-',
                    )
        ax.grid(True)

        plt.legend()
        plt.show()

    def get_value_in_field(self, value, x_min=0, x_max=10, r_min=0, r_max=3):
        """
        Return the value in the desired domain for the given field quantity.

        Parameters
        ----------
        value: pd.DataFrame
            The data to extract values from.
        x_min: int or float, optional
            Minimum value of x for the extraction. Default is 0.
        x_max: int or float, optional
            Maximum value of x for the extraction. Default is 10.
        r_min: int or float, optional
            Minimum value of r for the extraction. Default is 0.
        r_max: int or float, optional
            Maximum value of r for the extraction. Default is 3.

        Returns
        -------
        tuple
            The extracted x, r, and field values as numpy arrays.
        """
        self.__test_validity_input_field(x_min, x_max, r_min, r_max)

        x_min_idx, x_max_idx, r_min_idx, r_max_idx = self.__get_index(x_min, x_max, r_min, r_max)
        x_sub = self.x_grid[x_min_idx: x_max_idx]
        r_sub = self.r_grid[r_min_idx: r_max_idx]

        value_sub = value.iloc[x_min_idx: x_max_idx, r_min_idx: r_max_idx]
        return x_sub, r_sub, value_sub

    def __get_title(self, field: str, name_value: str) -> str:
        """
        Get the formatted title for a specific field and value name.
        """
        titles = {
            'total': {
                'ux': r"$\tilde{U}_x$", 'ur': r"$\tilde{U}_r$", 'ut': r"$\tilde{U}_\theta$",
                'rho': r"$\tilde{\rho}$", 'p': r"$\tilde{p}$", 'T': r"$\tilde{T}$"
            },
            'rans': {
                'ux': r"$U_x$", 'ur': r"$U_r$", 'ut': r"$U_\theta$", 'rho': r"$\rho$",
                'p': r"$p$", 'T': r"$T$"
            },
            'pse': {
                'Re(ux)': r"$\Re(u_x')$", 'Im(ux)': r"$\Im(u_x')$", 'abs(ux)': r"$|u_x'|$",
                'Re(ur)': r"$\Re(u_r')$", 'Im(ur)': r"$\Im(u_r')$", 'abs(ur)': r"$|u_r'|$",
                'Re(ut)': r"$\Re(u_\theta')$", 'Im(ut)': r"$\Im(u_\theta')$", 'abs(ut)': r"$|u_\theta'|$",
                'Re(rho)': r"$\Re(\rho')$", 'Im(rho)': r"$\Im(\rho')$", 'abs(rho)': r"$|\rho'|$",
                'Re(p)': r"$\Re(p')$", 'Im(p)': r"$\Im(p')$", 'abs(p)': r"$|p'|$",
                'Re(T)': r"$\Re(T')$", 'Im(T)': r"$\Im(T')$", 'abs(T)': r"$|T'|$"
            }
        }
        return titles[field][name_value]

    def __test_validity_input_field(self, x_min, x_max, r_min, r_max):
        """
        Return the value in the desired domain for the given field quantity.

        Parameters
        ----------
        value: pd.DataFrame
            The data to extract values from.
        x_min: int or float, optional
            Minimum value of x for the extraction. Default is 0.
        x_max: int or float, optional
            Maximum value of x for the extraction. Default is 10.
        r_min: int or float, optional
            Minimum value of r for the extraction. Default is 0.
        r_max: int or float, optional
            Maximum value of r for the extraction. Default is 3.

        Returns
        -------
        tuple
            The extracted x, r, and field values as numpy arrays.
        """
        if not isinstance(x_max, (float, int)) or not isinstance(r_max, (float, int)):
            raise TypeError("x_max and r_max must be an int or a float")
        if not isinstance(x_min, (float, int)) or not isinstance(r_min, (float, int)):
            raise TypeError("x_min and r_min must be an int or a float")

        if x_max < x_min:
            raise ValueError("x_min must be greater than x_max")
        if r_max < r_min:
            raise ValueError("r_max must be greater than r_min")

        min_of_x = np.argmin(self.x_grid)
        min_of_r = np.argmin(self.r_grid)
        if x_min < min_of_x:
            raise ValueError(f"x_max must be greater than or equal to {min_of_x}")
        if r_min < min_of_r:
            raise ValueError(f"r_max must be greater than or equal to {min_of_r}")

        max_of_x = np.argmax(self.x_grid)
        max_of_r = np.argmax(self.r_grid)
        if x_min > max_of_x:
            raise ValueError(f"x_max must be greater than or equal to {max_of_x}")
        if r_min > max_of_r:
            raise ValueError(f"r_max must be greater than or equal to {max_of_r}")

    def __get_field(self, name_value, field):
        """
        Return the value depending on the field selected in the plot methods.

        Parameters
        ----------
        name_value: str
            The specific quantity within the field.
        field: str
            The field type ('total', 'rans', 'pse').

        Returns
        -------
        pd.DataFrame
            The field values corresponding to the specified quantity and field type.
        """
        match field:
            case "total":
                if name_value not in PerturbationField.rans_quantities:
                    raise ValueError("quantity not valid - choose among", PerturbationField.rans_quantities)
                value = self.perturbation_field.compute_total_field(self.t, self.epsilon)[name_value]
            case 'rans':
                if name_value not in RansField.quantities:
                    raise ValueError("quantity not valid - choose among", RansField.quantities)
                value = self.perturbation_field.rans_values[name_value]
            case 'pse':
                if name_value not in PerturbationField.pse_quantities:
                    raise ValueError("quantity not valid - choose among", PerturbationField.rans_quantities)
                value = self.perturbation_field.values[name_value]
            case _:
                raise ValueError("the field you want to display is not available - choose between (total, rans or pse)")

        return value

    def __get_index(self, x_min, x_max, r_min, r_max):
        """
        Return the index of the wanted domain based on the provided x and r limits.

        Parameters
        ----------
        x_min: int or float
            Minimum value of x.
        x_max: int or float
            Maximum value of x.
        r_min: int or float
            Minimum value of r.
        r_max: int or float
            Maximum value of r.

        Returns
        -------
        tuple
            The indices corresponding to the specified x and r limits.
        """
        x_max_idx = np.where(self.x_grid <= x_max)[0][-1]
        x_min_idx = np.where(self.x_grid >= x_min)[0][0]
        r_max_idx = np.where(self.r_grid <= r_max)[0][-1]
        r_min_idx = np.where(self.r_grid >= r_min)[0][0]
        return x_min_idx, x_max_idx, r_min_idx, r_max_idx

    def __verbose(self):
        """
        Print reference values and Mach number if verbosity is enabled.

        This function displays information about the current post-processing scenario, including the Strouhal number,
        reference values, and the Mach case ID.
        """
        print(f"Post-processing for St = {self.St}")
        print(f"Reference Values: {get_reference_values()}")
        print(f"Case ID: {self.ID_MACH} Mach Reference: {get_mach_reference(self.ID_MACH)}")
