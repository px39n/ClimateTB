from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from .single_plot_func import *



def visualize_dataset(ds, date, fea_dict, save_path=None):

    ds=ds.sel(time=date)
    n_features = len(fea_dict)
    n_dates = len(date)
    fig = plt.figure(figsize=(1.7 * n_dates + 2, 1.7 * n_features))  # Add 2 to the width to accommodate colorbars
    gs = gridspec.GridSpec(n_features, n_dates + 1, figure=fig, hspace=0.01, wspace=0.01)
    
    for i, feature_name in tqdm(enumerate(fea_dict.keys())): 

        # Check if the feature name is in the dataset
        if feature_name in ds:
            ds_var = ds[feature_name]
        else:
            # Try removing _{number} from the feature name
            base_feature_name = feature_name.split('_')[0]
            matching_vars = [var for var in ds.variables if var.startswith(base_feature_name)]
            if matching_vars:
                ds_var = ds[matching_vars[0]]
            else:
                raise ValueError(f"Could not find {feature_name} or a similar variable in the dataset")
            ds_var=ds_var.copy()
            
        #ds_var=ds[feature_name]
        var_dict=fea_dict[feature_name]

        # Apply index if specified
        if 'index' in var_dict:
            index = fea_dict[feature_name]['index']
            ds_var = ds_var.isel(**index)
        # Apply convert if specified
        if 'convert' in var_dict:
            convert = var_dict['convert']
            if 'multiplier' in convert:
                ds_var *= convert['multiplier'] 
            if 'offset' in convert:
                ds_var += convert['offset']

        # Check if color_range is a list with length 2
        if 'range' in var_dict:
            color_range=var_dict['range']
            assert isinstance(color_range, list) and len(color_range) == 2, f"Invalid range for {color_range}."
        else:
            color_range = [ds_var.min().item(), ds_var.max().item()]


        def guess_cmap(feature_name):
            if feature_name in ["WS10","U10","V10","U","V","WS",
                                "sp","PSFC","SP", "T"]:
                cmap=plt.cm.RdYlBu_r

            elif feature_name in ["QVAPOR","TP"]:
                import matplotlib.colors as mcolors
                cmap = plt.cm.Blues
                #cmap2 = mcolors.ListedColormap(cmap(np.linspace(0.2, 1, 256))).colors
                #cmap = mcolors.ListedColormap(cmap2)
            else:
                cmap=plt.cm.jet
            return cmap

        # Check if cmap is specified
        if 'cmap' in var_dict:
            cmap=var_dict['cmap']
        else:
            cmap=guess_cmap(feature_name)
        for j, single_date in enumerate(date):
            ds_var_time=ds_var.sel(time=single_date)
            ax = plt.subplot(gs[i, j])    

            var_dict['func_args'] = [{} if arg is None else arg for arg in var_dict['func_args']]

            if plot_single_ds in var_dict['func']:
                k = var_dict['func'].index(plot_single_ds)
                plot_single_ds(ax,ds_var_time,color_range,cmap,**var_dict['func_args'][k])
            
            if plot_maxima in var_dict['func']:
                k = var_dict['func'].index(plot_maxima)
                plot_maxima(ax,ds_var_time,**var_dict['func_args'][k])

            if draw_contour in var_dict['func']:
                k = var_dict['func'].index(draw_contour)
                draw_contour(ax,ds_var_time,color_range,**var_dict['func_args'][k])

            if draw_wind_quiver in var_dict['func']:
                k = var_dict['func'].index(draw_wind_quiver)
                U10=ds[var_dict['vector'][0]].sel(time=single_date)
                V10=ds[var_dict['vector'][1]].sel(time=single_date)
                draw_wind_quiver(ax,U10,V10,**var_dict['func_args'][k])

           
            # ax.set_xlim([118, 122.5])
            # ax.set_ylim([27, 31.5])
            # xxrange = np.arange(119, 123, 2)
            # yyrange = np.arange(27.5, 31.5, 1.5)
            # ax.set_xticks(xxrange)
            # ax.set_yticks(yyrange)
            xxrange = ax.get_xticks()
            yyrange = ax.get_yticks()
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.1f}°E"))
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, p: f"{y:.1f}°N"))
            # ax.axis('on')
            # Inside your loop

            # The below is for the label and title
            if j == 0:  # For the leftmost subplots
                ax.tick_params(axis="y", labelleft=True, length=5)
                ax.set_ylabel(f"{var_dict['str']} ({var_dict['unit']})") 
            else:
                ax.tick_params(axis="y", labelleft=False, labelright=False, length=0)
            if i==0:
                ax.set_title(pd.to_datetime(single_date).strftime('%m-%d %H:%M'))
            elif i == n_features - 1:  # For the bottom subplots
                ax.tick_params(axis="x", labelbottom=True, length=5) 
            else:
                ax.tick_params(axis="x", labelbottom=False, labeltop=False, length=0)
                
        # Add colorbar
        ax = plt.subplot(gs[i, -1])  # Select the last column for the colorbar        
        plot_add_colorbar(ax,cmap, color_range,font_size=10)
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.show()


    return