import os
import sys
from pathlib import Path
import xarray as xr
# import pandas as pd

from src.utils import compute_A

# # Combine all files in path 
# # select var 
# var = 'tas'cond
# sim_number = 0

# # select lat, lon and 
# reduce = 'max' #  max min mean, daily data
# lat = 41.881832 # latitude
# lon = -87.623177 % 360 # for longitudes take the value modulo 360


var = str(sys.argv[1]) # tas
sim_number = int(sys.argv[2]) # simulation number
reduce = str(sys.argv[3]) # max
lat = float(sys.argv[4]) # latitude
lon = float(sys.argv[5]) % 360# longitude

print(var, sim_number, reduce, lat, lon)

# slelect window size
spatial_window_size = 2 # region around the lat, lon
# temporal_window_size = 7
path = f"/glade/derecho/scratch/awikner/PLASIM/data/2000_year_sims_new/sim{sim_number}/{var}/"

files = [f for f in os.listdir(path) if f.endswith('gaussian.nc')]
# files = files[:]
# Remove spin-off data: take file only if year >10
files = [f for f in files if int(f.split('_')[0])>10]
# # order the files by year
files = sorted(files, key=lambda x: int(x.split('_')[0]))

# disable the printing of the warning
# # combine all files using compute_A as a preprocessing function 
A = xr.open_mfdataset([path+file for file in files], preprocess=lambda ds: compute_A(ds, var, lat, lon, spatial_window_size, reduce), combine='nested',
                       concat_dim='time', parallel=True, decode_times=True, use_cftime=True)
# A = xr.open_mfdataset([path+file for file in files], preprocess=lambda ds: compute_A(ds, var, lat, lon, spatial_window_size, reduce), combine='nested',
                    #    concat_dim='time', parallel=True, decode_times=True, use_cftime=True, engine=h5netcdf)
# h5netcdf

A_df = A.to_dataframe()
# save the dataframe

# Make folder to save the data
SAVE_DIR = f'data/ground_truth/sim{sim_number}/'
Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)

# save the dataframe
file_name = f'{var}_lat.{int(lat)}_lon.{int(lon)}_spatial.{spatial_window_size}_reduce.{reduce}.csv'
if os.path.exists(SAVE_DIR + file_name):
    os.remove(SAVE_DIR + file_name)
A_df.to_csv(SAVE_DIR + file_name)