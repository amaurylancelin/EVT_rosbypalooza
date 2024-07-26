import numpy as np

def compute_A(ds, var, lat, lon, spatial_window_size, reduce='max'):
    # for longitudes take the value modulo 360
    if lon < 0:
        lon = lon % 360
    # get the index of the lat and lon
    lat_idx = np.abs(ds.lat.values - lat).argmin()
    lon_idx = np.abs(ds.lon.values - lon).argmin()

    # compute on observable A being the average temperature in the window over the last the temporal_window_size days
    A = ds.isel(lat=slice(lat_idx-spatial_window_size, lat_idx+spatial_window_size), 
                           lon=slice(lon_idx-spatial_window_size, lon_idx+spatial_window_size))

    if reduce == 'mean':
        A = A.resample(time='D').mean()
    elif reduce == 'max':
        A = A.resample(time='D').max()
    elif reduce == 'min':
        A = A.resample(time='D').min()
    elif reduce == 'None':
        pass
    else:
        raise ValueError("reduce must be either 'mean', 'max', 'min', or 'None'")
    A = A[var].mean(dim=['lat', 'lon'])# check window_size *4 or not #.rolling(time=temporal_window_size)
    return A