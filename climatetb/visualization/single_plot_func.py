import numpy as np
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import xarray as xr  # Assuming x_predicted and zhejiang are xarray DataArrays or Datasets
import warnings
from scipy.stats import gaussian_kde
from scipy.interpolate import UnivariateSpline
 
def draw_wind_quiver(ax, u10, v10, scale=140, width=0.007, density=10,legend=10):
    try:
        longitude = u10.longitude.values[::density]
        latitude = u10.latitude.values[::density]
        u10_values = u10.values[::density, ::density]
        v10_values = v10.values[::density, ::density]
    except AttributeError:
        print("DataArray must contain longitude and latitude values.")
        return
    lon, lat = np.meshgrid(longitude, latitude)
    ax.quiver(lon, lat, u10_values, v10_values, scale=scale, width=width)

    rp=[0.87, 0, 0.13, 0.11]
    # Add a rectangle to the bottom right corner of the plot
    ax.add_patch(plt.Rectangle((rp[0], rp[1]), 
                               rp[2], rp[3], 
                               transform=ax.transAxes, facecolor='white', edgecolor='black', alpha=1))
    arrow_position = [rp[0] + rp[2] / 2 - 0.04, rp[1] + rp[3] * 2 / 3+ 0.01]
    text_position = [rp[0] + rp[2] / 2, rp[1] + rp[3] / 3]
    ax.quiver(arrow_position[0], arrow_position[1], 0.07, 0, scale=0.8, transform=ax.transAxes)
    # Calculate legend position based on text position
    # Calculate wind speed for the legend arrow
    arrow_length = 0.07  # Length of the arrow in axis coordinates
    arrow_speed = arrow_length * scale/0.4
    legend = round(arrow_speed, 1)  # Round to 1 decimal place
    ax.text(text_position[0], text_position[1], f"{legend}", transform=ax.transAxes, fontsize=6, va='center', ha='center')

    return ax



def draw_contour(ax, ds_masked, color_range, color='black', linewidth=.5, interval=40, label=True):
    # Extract the longitude, latitude, and data values from the DataArray
    lon = ds_masked.coords['longitude'].values
    lat = ds_masked.coords['latitude'].values
    data = ds_masked.values

    # Create a contour plot
    contour = ax.contour(lon, lat, data, levels=np.arange(color_range[0], color_range[1], interval), colors=color, linewidths=linewidth)

    if label:
        ax.add_patch(plt.Rectangle((0.87, 0), 0.15, 0.1, transform=ax.transAxes, facecolor='white', edgecolor='black', alpha=0.7))
        # Add text to the rectangle indicating the interval
        ax.text(0.89, 0.03, f"{interval}", transform=ax.transAxes, fontsize=8 - 0.1*len(str(interval)), va='center')

    return ax

import tcmarkers
def plot_maxima(ax, ds_masked, color="black", pt_size=4, circle_color="black", 
                threshold=20, circle=True, min=False, marker="hurricane",alpha=0.3):
    data_array = ds_masked.values
    total_pixels = len(ds_masked.coords['longitude']) * len(ds_masked.coords['latitude']) 
    # Find the coordinates of the maximum/minimum point, ignoring NaN values
    maxima_index = np.nanargmin(data_array) if min else np.nanargmax(data_array)
    maxima_coords = np.unravel_index(maxima_index, data_array.shape)

    # Convert the index coordinates to longitude and latitude
    lon = ds_masked.coords['longitude'].values[maxima_coords[1]]
    lat = ds_masked.coords['latitude'].values[maxima_coords[0]]
    
    # Check if the maximum/minimum value is greater/lower than the threshold
    if (min and data_array[maxima_coords] < threshold) or \
       (not min and data_array[maxima_coords] > threshold):
        # Count the number of values greater/lower than the threshold, ignoring NaN values
        count = np.nansum((data_array < threshold) if min else (data_array > threshold))
        
        # If circle is True and count > 5, draw a circle
        if circle and count > 5:
            # Calculate the radius so that the area of the circle is proportional to the count
            radius = np.sqrt(count / total_pixels / np.pi)           
            # Draw a circle around the maximum point
            ax.add_patch(plt.Circle((lon, lat), radius, linewidth=0.5, color=circle_color, fill=False))
    
        # Plot the maximum point
        marker_style = tcmarkers.HU if marker == "hurricane" else None
        facecolors = color
        ax.scatter(lon, lat, color=color, s=pt_size, marker=marker_style, 
                   edgecolors=color, facecolors=facecolors, zorder=3,alpha=alpha)

    return ax, lon, lat


def plot_single_ds(ax, ds, color_range=None, cmap=plt.cm.RdYlGn, alpha=1, min=None, max=None, norm=None):
    ax.tick_params(axis="x", labelbottom=False)
    ax.tick_params(axis="y", labelleft=False)
    data_array = ds.values
    try:
        longitude = ds.longitude.values
        latitude = ds.latitude.values
    except AttributeError:
        print("Dataset must contain longitude and latitude values.")
        return

    # Create a mask for values within the specified range
    mask = np.ones_like(data_array, dtype=bool)  # default mask is all True
    if min is not None:
        mask &= (data_array >= min)
    if max is not None:
        mask &= (data_array <= max)
    data_array = np.where(mask, data_array, np.nan)  # Replace out-of-range values with NaN

    lon, lat = np.meshgrid(longitude, latitude)
    if color_range:
        c = ax.pcolormesh(lon, lat, data_array, cmap=cmap, vmin=color_range[0], vmax=color_range[1], alpha=alpha, norm=norm)
    else:
        c = ax.pcolormesh(lon, lat, data_array, cmap=cmap, alpha=alpha, norm=norm)
    return ax


def plot_add_colorbar(ax,cmap,color_range,font_size=15):
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
 
    
    ax.tick_params(axis="x", labelbottom=False, labeltop=False, length=0)
    ax.tick_params(axis="y", labelleft=False, labelright=False, length=0)    
    # Create an inset axes for the colorbar at 1/4 position of width
    cax = inset_axes(ax,
                     width="7.5%",  # colorbar width
                     height="90%",  # colorbar height
                     loc='lower left',  # position of colorbar
                     bbox_to_anchor=(0.1, 0.05, 1, 1),  # positioning of colorbar within axes
                     bbox_transform=ax.transAxes,  # use axes coordinate system
                     borderpad=0,
                     )
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    if color_range is not None:
        norm = mpl.colors.Normalize(vmin=color_range[0], vmax=color_range[1])
        cbar = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, orientation='vertical')
        cbar.ax.tick_params(labelsize=font_size)


def guess_cmap(feature_name):
    if feature_name in ["WS10","U10","V10","U","V","WS",
                        "sp","PSFC","SP"]:
        cmap=plt.cm.RdYlBu_r

    elif feature_name in ["QVAPOR","TP"]:
        import matplotlib.colors as mcolors
        cmap = plt.cm.Blues
        #cmap2 = mcolors.ListedColormap(cmap(np.linspace(0.2, 1, 256))).colors
        #cmap = mcolors.ListedColormap(cmap2)
    else:
        plt.cm.jet
    return cmap
