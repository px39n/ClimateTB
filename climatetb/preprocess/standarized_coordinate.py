import xarray as xr

def standardize_coordinates(ds):
    longitude_candidates = ["XLONG", "west_east", "WEST_EAST", "xlong", "XLONG_U", "XLONG_V"]
    latitude_candidates = ["XLAT", "south_north", "SOUTH_NORTH", "xlat", "XLAT_U", "XLAT_V"]
    time_candidates = ["Time","XTIME","Xtime"]
    def process_dimension(candidates, dim_type,ds):
        matches_dim = [var for var in candidates if var in ds.dims]


        if len(matches_dim) > 1:
            raise ValueError(f"Multiple {dim_type} candidates found: {matches_dim}")
      
        if len(matches_dim) == 0:
            return ds
        
        candidate_dim = matches_dim[0]
        #print({candidate_dim:dim_type})
        ds = ds.rename({candidate_dim:dim_type})
        
        matches_coord = [var for var in candidates if var in ds.coords]
        if len(matches_coord) == 0:    # If there is no coordinate, we can assign the coordinate directly
            pass
        else:    
            candidate_coord = matches_coord[0]
            if ds[candidate_coord].ndim > 1:
                coordinate_values = ds[candidate_coord].isel(**{dim: 0 for dim in ds[candidate_coord].dims if dim != dim_type}).values
                ds = ds.assign_coords({dim_type: coordinate_values})
                ds[dim_type].attrs = ds[candidate_coord].attrs
            else:
                ds = ds.assign_coords({dim_type: ds[candidate_coord]})
                ds = ds.assign_attrs({dim_type: ds[candidate_coord].attrs})

            ds = ds.drop_vars([candidate_coord])

            
        return ds
    ds=process_dimension(time_candidates, 'time',ds)
    ds=process_dimension(longitude_candidates, 'longitude',ds)
    ds=process_dimension(latitude_candidates, 'latitude',ds)


    ds = ds.isel(time=~ds.get_index('time').duplicated())
    ds = ds.isel(longitude=~ds.get_index('longitude').duplicated())
    ds = ds.isel(latitude=~ds.get_index('latitude').duplicated())
    return ds

#ds = ds.assign_coords(west_east=ds.XLONG.isel(Time=0, south_north=0).values)
#ds=ds.set_index({"Time":"XTIME"})
# Example usage:
#ds = standardize_coordinates(ds)