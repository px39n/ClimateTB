import xarray as xr
def process_wind(ds):
    wind_components = {
        ('U10', 'V10'): 'WS10',
        ('U', 'V'): 'WS',
        ('U20', 'V20'): 'WS20',
        ('U30', 'V30'): 'WS30',
        ('U40', 'V40'): 'WS40',
        ('U50', 'V50'): 'WS50'
    }
    for (u_comp, v_comp), wind_speed_name in wind_components.items():
        if u_comp in ds and v_comp in ds:
            u_dims = ds[u_comp].dims
            v_dims = ds[v_comp].dims
            if u_dims == v_dims and len(u_dims) <= 3:
                ds[wind_speed_name] = (ds[u_comp]**2 + ds[v_comp]**2)**0.5
                print(f"Calculated {wind_speed_name} from {u_comp} and {v_comp}")

    if not any(all(comp in ds for comp in pair) for pair in wind_components):
        print("No matching wind components found in the dataset.")

    return ds
