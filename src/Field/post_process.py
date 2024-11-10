import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, ticker

from src.Field.perturbation_field import PerturbationField
from src.Field.rans_field import RansField
from src.ReadData.read_info import get_reference_values
from src.ReadData.read_mach import get_mach_reference
from src.ReadData.read_radius import get_r_grid
from src.toolbox.fig_parameters import RANS_FIGSIZE


class PostProcess:
    titles = {
            "rho": r"$\hat{\rho}$",
            "Re(rho)": r"$\Re{\rho'}$",
            "Im(rho)": r"$\Im{\rho'}$",
            "abs(rho)": r"$|{\rho'}|$",

            "ux": r"$\hat{u_x}$",
            "Re(ux)": r"$\Re(u_x')$",
            "Im(ux)": r"$\Im(u_x')$",
            "abs(ux)": r"$|u_x'|$",

            "ur": r"$\hat{u_r'}$",
            "Re(ur)": r"$\Re(u_r')$",
            "Im(ur)": r"$\Im(u_r')$",
            "abs(ur)": r"$|u_r'|$",

            "ut": r"$\hat{u_\theta}$",
            "Re(ut)": r"$\Re(u_\theta')$",
            "Im(ut)": r"$\Im(u_\theta')$",
            "abs(ut)": r"$|u_\theta'|$",

            "T": r"$\hat{T}$",

            "p": r"$\hat{p}$",
            "Re(p)": r"$\Re(p')$",
            "Im(p)": r"$\Im(p')$",
            "abs(p)": r"$|p|$",
            "mean(p)": "Stoechastic Mean p"
    }

    def __init__(self, St: float, ID_MACH: int, t: [int, float] = 0, epsilon: [int, float] = 0.01, verbose: bool = False) -> None:

        if not isinstance(St, (int, float)) or St <= 0:
            raise ValueError("St must be a positive float or integer")
        if not isinstance(ID_MACH, int) or ID_MACH <= 0:
            raise ValueError("ID_MACH must be a positive integer")

        self.St = St
        self.ID_MACH = ID_MACH
        self.epsilon = epsilon
        self.t = t
        self.rans_field = RansField(ID_MACH)
        self.pert_field = PerturbationField(St, ID_MACH)
        if verbose:
            self.__verbose()

    def get_fields_stats(self, quantity: str = None) -> pd.DataFrame | dict[str, pd.DataFrame]:

        if not isinstance(quantity, str):
            raise TypeError("quantity must be a string")

        if quantity and quantity not in self.rans_field.quantities:
            raise ValueError(f"{quantity} is not a valid quantity - chose between {self.rans_field.quantities}")

        stats_dict = {}
        rans_values = self.pert_field.rans_values
        if quantity:
            return pd.DataFrame(rans_values[quantity].describe())
        else:
            for quantity in self.rans_field.quantities:
                stats = rans_values[quantity].describe()
                stats_dict[quantity] = stats

        return pd.DataFrame(stats_dict)

    def plot_alpha(self):
        x_grid = self.pert_field.x_grid
        stability_data = self.pert_field.get_stability_data()
        fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
        ax0.plot(x_grid, stability_data["Re(alpha)"], title=r"$\alpha_r$")
        ax1.plot(x_grid, stability_data["Im(alpha)"], title=r"$\alpha_i$")
        ax0.get_legend().remove()
        ax1.get_legend().remove()
        fig.tight_layout()
        plt.show()

    def plot_field(self, name_value, field: "str" = "total", x_min=0, x_max=10, r_min=0, r_max=5, t=0):
        """

        Parameters
        ----------
        name_value: str
            value to plot. Available : -contourf : "rho","ux", "ur", "T", "P"
                                       -iso-contour : abs(q") and Re(q")

        x_max: int or float - optional
        r_max: int or float - optional
            provide the limit of the domain to plot the values

        Returns
        -------
        None
        """
        if not isinstance(field, str):
            raise TypeError("field must be a string between 'total', 'rans' and 'pse'")

        self.__test_validity_input_field(x_min, x_max, r_min, r_max)
        match field:
            case "total":
                if name_value not in self.rans_field.quantities:
                    raise ValueError("quantity not valid - choose among", self.rans_field.quantities)
                value = self.pert_field.compute_total_field(self.t, self.epsilon)[name_value]
            case "rans":
                if name_value not in self.rans_field.quantities:
                    raise ValueError("quantity not valid - choose among", self.rans_field.quantities)
                value = self.pert_field.rans_values[name_value]

            case "pse":
                if name_value not in PerturbationField.pse_quantities:
                    raise ValueError("quantity not valid - choose among", PerturbationField.pse_quantities)
                value = PerturbationField.convert_to_rans_reference(self.pert_field.values, self.ID_MACH)[name_value]
                # value = self.pert_field.values[name_value]
            case _:
                raise ValueError("the field you want to display is not available - choose between (total, rans or pse)")

        x, r, value_sub = self.get_value_in_field(value, x_min=x_min, x_max=x_max, r_min=r_min, r_max=r_max)
        plt.style.use("ggplot")
        fig, ax = plt.subplots(figsize=RANS_FIGSIZE, layout="constrained")


        cs = ax.contourf(x, r, value_sub.transpose(), levels=100, cmap="jet")


        plt.xlabel("x/D")
        plt.ylabel("r/D")
        tick_spacing = 1
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        ax.set_title(self.titles[name_value])
        cbar = fig.colorbar(cs)
        tick_locator = ticker.MaxNLocator(nbins=5)
        cbar.locator = tick_locator
        cbar.set_ticks(ticks=tick_locator, vmin=value.min(), vmax=value.max())
        cbar.update_ticks()
        plt.show()

    def get_value_in_field(self, value, x_min=0, x_max=10, r_min=0, r_max=3):
        """
        Return the value in the wanted domain
        """

        self.__test_validity_input_field(x_min, x_max, r_min, r_max)

        r_grid = get_r_grid()
        x_grid = self.pert_field.x_grid

        x_min_idx, x_max_idx, r_min_idx, r_max_idx = self.__get_index(x_min, x_max, r_min, r_max)
        x_sub = x_grid[x_min_idx: x_max_idx]
        r_sub = r_grid[r_min_idx: r_max_idx]

        value_sub = value.iloc[x_min_idx: x_max_idx, r_min_idx: r_max_idx]
        return x_sub, r_sub, value_sub

    def __test_validity_input_field(self, x_min, x_max, r_min, r_max):
        if not isinstance(x_max, (float, int)) or not isinstance(r_max, (float, int)):
            raise TypeError("x_max and r_max must be an int or a float")
        if not isinstance(x_min, (float, int)) or not isinstance(r_min, (float, int)):
            raise TypeError("x_min and r_min must be an int or a float")

        if x_max < x_min:
            raise ValueError("x_min must be greater than x_max")
        if r_max < r_min:
            raise ValueError("r_max must be greater than r_min")

        x_grid = self.pert_field.x_grid
        r_grid = get_r_grid()

        min_of_x = np.argmin(x_grid)
        min_of_r = np.argmin(r_grid)
        if x_min < min_of_x:
            raise ValueError(f"x_max must be greater than or equal to {min_of_x}")
        if r_min < min_of_r:
            raise ValueError(f"r_max must be greater than or equal to {min_of_r}")

        max_of_x = np.argmax(x_grid)
        max_of_r = np.argmax(r_grid)
        if x_min > max_of_x:
            raise ValueError(f"x_max must be greater than or equal to {max_of_x}")
        if r_min > max_of_r:
            raise ValueError(f"r_max must be greater than or equal to {max_of_r}")

    def __verbose(self):
        print(f"Reference values for the case k={self.ID_MACH}:")
        print(get_reference_values().loc[self.ID_MACH].to_string())
        print(get_mach_reference().loc[self.ID_MACH].to_string())

    def __get_index(self, x_min, x_max, r_min, r_max):
        x_grid = self.pert_field.x_grid
        r_grid = get_r_grid()
        x_max_idx = np.where(x_grid <= x_max)[0][-1]
        x_min_idx = np.where(x_grid >= x_min)[0][0]
        r_max_idx = np.where(r_grid <= r_max)[0][-1]
        r_min_idx = np.where(r_grid >= r_min)[0][0]
        return x_min_idx, x_max_idx, r_min_idx, r_max_idx
