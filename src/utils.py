import numpy as np
from datetime import datetime, timedelta
import netCDF4 as nc
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


def extract_data(nc_file_path, file_ind, var, latitude, longitude, reduce='max', spatial_window_size=2):

    if var == 'hus':
        filename_end = 'gaussian_postproc.nc'
    else:
        filename_end = 'gaussian.nc'

    # Open the netCDF file
    if var == 'precip':
        ds = nc.Dataset(nc_file_path + '/prc/' +str(file_ind) + '_' + filename_end)
        ds2 = nc.Dataset(nc_file_path + '/prl/' +str(file_ind) + '_' + filename_end)
    else:
        ds = nc.Dataset(nc_file_path + f'/{var}/' +str(file_ind) + '_' + filename_end)
    
    # Extract the data
    lats = ds.variables['lat'][:]
    lons = ds.variables['lon'][:]
    times = ds.variables['time'][:]

    if var == 'precip':
        # Precipitation is in m/s (units of dt in seconds - dt is assumed 6 hrs)
        var_data = (ds.variables['prc'][:] + ds2.variables['prl'][:])*(6*60*60)
    else:
        var_data = ds.variables[var][:]

    # Convert time to datetime objects assuming time is in hours since some reference point
    time_units = ds.variables['time'].units
    base_time_str = time_units.split('since')[1].strip()
    if var == 'hus':
        formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']
        for format in formats:
            try:
                base_time = datetime.strptime(base_time_str.split('.')[0], format)
            except ValueError:
                continue
    else:
        base_time = datetime.strptime(base_time_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
    dates = np.array([base_time + timedelta(hours=int(t)) for t in times])
    
    # Convert time to days (ignoring the time part for simplicity)
    days = np.array([d.date() for d in dates])
    
    # Find the closest grid point
    lat_idx = np.abs(lats - latitude).argmin()
    lon_idx = np.abs(lons - longitude).argmin()
    
    # Initialize a list to store daily max values along with dates
    daily_max_values = []
    
    # Loop over each unique day
    unique_days = np.unique(days)
    for day in unique_days:
        # Get the indices for the current day
        day_indices = np.where(days == day)
        
        # Extract the 3x3 grid around the closest grid point
        lat_indices = slice(max(lat_idx - spatial_window_size-1, 0), min(lat_idx + spatial_window_size, len(lats)))
        lon_indices = slice(max(lon_idx - spatial_window_size-1, 0), min(lon_idx + spatial_window_size, len(lons)))
        
        # Get the maximum/minimum/average value in the 3x3 grid for the current day
        if var == 'hus':
            if reduce == 'max':
                daily_data = np.max(var_data[day_indices][:, 2, lat_indices, lon_indices]) # 850 hPa
            elif reduce == 'min':
                daily_data = np.min(var_data[day_indices][:, 2, lat_indices, lon_indices])
            elif reduce == 'mean':
                daily_data = np.mean(var_data[day_indices][:, 2, lat_indices, lon_indices])

        else:
            if reduce == 'max':
                daily_data = np.max(var_data[day_indices][:, lat_indices, lon_indices])
            elif reduce == 'min':
                daily_data = np.min(var_data[day_indices][:, lat_indices, lon_indices])
            elif reduce == 'mean':
                daily_data = np.mean(var_data[day_indices][:, lat_indices, lon_indices])
        
        # Append the date and the result to the list
        daily_max_values.append((day, daily_data))
    
    ds.close()
    return daily_max_values