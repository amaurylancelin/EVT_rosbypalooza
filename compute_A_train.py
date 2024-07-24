import xarray as xr
import os
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('darkgrid')
import pandas as pd
import cartopy.crs as ccrs
from metpy.units import units
from tqdm import tqdm
from src.utils import compute_A


# Combine all files in path 
# select var 
var = 'tas'
sim_number = 0
path = f"/glade/derecho/scratch/awikner/PLASIM/data/2000_year_sims_new/sim{sim_number}/{var}/"
# select lat, lon and window size
spatial_window_size = 2
# temporal_window_size = 7
reduce = 'max'
# Select lat and lon of Chicago
lat = 41.881832
lon = -87.623177 % 360 # for longitudes take the value modulo 360


files = [f for f in os.listdir(path) if f.endswith('gaussian.nc')]
files = files[:]
# take file only if year >100
files = [f for f in files if int(f.split('_')[0])>10]
# sort the files by year
files = sorted(files, key=lambda x: int(x.split('_')[0]))

# disable the printing of the warning
# # combine all files using compute_A as a preprocessing function 
A = xr.open_mfdataset([path+file for file in files], preprocess=lambda ds: compute_A(ds, lat, lon, spatial_window_size, reduce), combine='nested',
                       concat_dim='time', parallel=True, decode_times=True, use_cftime=True)

A_df = A.to_dataframe()
# save the dataframe
file_name = f'data/train/A_{var}_lat.{int(lat)}_lon.{int(lon)}_spatial.{spatial_window_size}_reduce.{reduce}.csv'
if os.path.exists(file_name):
    os.remove(file_name)
A_df.to_csv(file_name)