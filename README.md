

# ClimateTB: A Python Package for Climate Data Visualization

ClimateTB is a powerful Python package designed for preprocessing and visualizing climate data. This tutorial will guide you through the main features and usage of ClimateTB.




**Check hw4.ipynb** (A homework examplein Notre Dame University: Applied Atmosphere) for more tutorials.




## Installation

To install ClimateTB, you can use pip:

```bash
pip install climatetb
```

## Importing ClimateTB

After installation, you can import the necessary modules:

```python
import climatetb as ctb
```

## Data Preprocessing

### Standardizing Coordinates

ClimateTB provides a function to standardize coordinates in your climate datasets:

```python
from climatetb.preprocess import standardize_coordinates

standardized_ds = standardize_coordinates(your_dataset)
```

This function attempts to rename and standardize the coordinate names for longitude, latitude, and time dimensions. It handles various common naming conventions used in climate data.

### Processing Wind Data

To calculate wind speed from U and V components:

```python
from climatetb.preprocess import process_wind

processed_ds = process_wind(your_dataset)
```

This function automatically detects wind components (U10, V10, U, V, etc.) and calculates the corresponding wind speed.

## Data Visualization

### Single Plot Functions

ClimateTB offers several functions for creating individual plots:

1. Wind Quiver Plot:

```python
from climatetb.visualization import draw_wind_quiver

fig, ax = plt.subplots()
draw_wind_quiver(ax, u10, v10)
```

2. Contour Plot:

```python
from climatetb.visualization import draw_contour

fig, ax = plt.subplots()
draw_contour(ax, your_data, color_range=[min_value, max_value])
```

3. Plotting Maxima:

```python
from climatetb.visualization import plot_maxima

fig, ax = plt.subplots()
plot_maxima(ax, your_data, threshold=20)
```

4. Single Dataset Plot:

```python
from climatetb.visualization import plot_single_ds

fig, ax = plt.subplots()
plot_single_ds(ax, your_data, color_range=[min_value, max_value])
```

### Grid Visualization

For a comprehensive visualization of multiple features across different time steps:

```python
from climatetb.visualization import visualize_dataset

fea_dict = {
    'WS10': {
        'str': 'Wind Speed',
        'unit': 'm/s',
        'func': [plot_single_ds, plot_maxima, draw_contour],
        'func_args': [{}, {'threshold': 20}, {'interval': 5}],
        'range': [0, 30],
        'vector': ['U10', 'V10']
    },
    # Add more features as needed
}

visualize_dataset(your_dataset, date_range, fea_dict, save_path='output.png')
```

This function creates a grid of plots for each feature and time step, applying the specified visualization functions and parameters.

## Advanced Usage

### Custom Color Maps

You can specify custom color maps for your visualizations:

```python
import matplotlib.pyplot as plt

custom_cmap = plt.cm.RdYlBu_r
fea_dict['YourFeature']['cmap'] = custom_cmap
```

### Data Conversion

To apply conversions to your data before plotting:

```python
fea_dict['Temperature'] = {
    'convert': {'multiplier': 1, 'offset': -273.15},  # Convert from Kelvin to Celsius
    # other parameters...
}
```
### Index

To apply the index to your high dimensional data, such as pressure level or bottomtop data:

```python
fea_dict['Temperature']['index'] = {'bottom_top':1}
```