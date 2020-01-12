import numpy
import pandas
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot
from scipy.interpolate import Rbf, NearestNDInterpolator

import utils
import constants


class ContourConfig(object):
    """Plot configuration specifications"""

    def __init__(self, data, title, **kwargs):
        self.data               = data
        self.title              = title
        self.colormap_path      = kwargs.get("colormap_path")
        self.colormap           = utils.read_colormap(self.colormap_path)
        self.colorbar_bounds    = kwargs.get("colorbar_bounds", [0, 0.75])
        self.colorbar_levels    = kwargs.get("colorbar_levels", 33)
        self.colorbar_label     = kwargs.get("colorbar_label", "Cp")

    
    def set_colormap_path(self, filename):
        self.colormap_path  = filename
        self.colormap       = utils.read_colormap(filename)


class ContourPlot(object):
    """2D contour plot of 3D data interpolated onto a discretized grid"""

    def __init__(self, title, grid_path, configs=[], **kwargs):
        self.title          = title
        self.grid           = None
        self.triangulation  = None
        self.border         = None
        self.set_grid_path(grid_path)
        self.set_configs(configs)
        
    
    def set_grid_path(self, filename):
        """Set the grid to interpolate onto"""

        (grid, triangulation, axes, border) = utils.read_stl(filename, triangulation=True)
        self.grid_path                      = filename
        self.grid                           = grid
        self.triangulation                  = triangulation
        self.axes                           = axes
        self.border                         = border
        self.margin                         = 0.5


    def set_configs(self, configs):
        """Set the configs (data and plot attributes)"""

        self.configs    = configs
        for config in configs:
            data            = config.data
            func            = Rbf(data.x, data.y, data.z, data.value.astype(float))
            values          = func(self.grid[:, 0], self.grid[:, 1], self.grid[:, 2])
            interp          = pandas.DataFrame(columns=constants.XYZ, data=self.grid)
            interp["value"] = values
            levels          = numpy.linspace(
                                config.colorbar_bounds[0], 
                                config.colorbar_bounds[1], 
                                config.colorbar_levels)

            # Update the config specification
            config.data             = interp
            config.colorbar_levels  = levels



    def render(self):
        """Render the matplotlib figure"""        

        # Initialize the matplotlib figure
        figure  = pyplot.figure(figsize=(16, 9), dpi=100)
        axes    = figure.subplots(len(self.configs), sharex=True)
        if not isinstance(axes, (list, numpy.ndarray)):
            axes    = [axes]

        xlim    = [self.grid[:, self.axes[0]].min() - self.margin, 
                    self.grid[:, self.axes[0]].max() + self.margin]
        ylim    = [self.grid[:, self.axes[1]].min() - self.margin, 
                    self.grid[:, self.axes[1]].max() + self.margin]

        for i, config in enumerate(self.configs):
            axes[i].set_aspect("equal")
            axes[i].axis("off")
            axes[i].set_title(config.title, fontsize=8)

            axes[i].plot(
                self.border[:, self.axes[0]], 
                self.border[:, self.axes[1]], 
                "-k",
                linewidth=0.5)

            contour = axes[i].tricontourf(
                self.triangulation, 
                config.data.value,
                extend="both",
                cmap=config.colormap,
                levels=config.colorbar_levels)
           
            axes[i].tricontour(
                self.triangulation,
                config.data.value,
                extend="both",
                levels=config.colorbar_levels,
                linewidths=0.5,
                colors="k")
           
            colorbar = figure.colorbar(contour, ax=axes[i])
            colorbar.ax.set_title(config.colorbar_label)

            axes[i].set_xlim(xlim)
            axes[i].set_ylim(ylim)

        return figure


    def save(self, filename):
        """Render the figure and save to file"""

        figure  = self.render()
        if figure:
            figure.savefig(filename, bbox_inches="tight")
            pyplot.close("all")














