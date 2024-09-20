import glob
import numpy as np
from rich.progress import track
import shutil
import sys
import xarray as xr

from utils import _convert_time
#path = '/home/augustinm/work/a-profiles/data/v-profiles/**/AP*.nc'
path = sys.argv[1]

# list all files
apro_files =  glob.glob(path, recursive=True)

for apro_file in track(apro_files, description="Processing"):
    # open the file
    ds = xr.open_dataset(apro_file, decode_times=False)

    # add altitude direction
    ds["altitude"] = ds["altitude"].assign_attrs({
        'positive': "up"
    })
    
    # convert time: from milliseconds to days
    ds = _convert_time(ds)
    
    # convert int64 to int32
    encoding = {}
    for varname, var in ds.variables.items():
        if var.dtype == np.int64:
            encoding[varname] = {"dtype": np.int32}
    
    # write the file
    ds.to_netcdf("tmp.nc", mode='w', encoding=encoding)
    shutil.move("tmp.nc", apro_file)
