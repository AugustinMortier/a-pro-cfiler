import glob
import numpy as np
import os
from rich.progress import track
import sys
import shutil
import xarray as xr

from utils import _convert_time
#path = '/home/augustinm/work/a-profiles/data/v-profiles/**/AP*.nc'
path = sys.argv[1]

# list all files
apro_files =  glob.glob(path, recursive=True)
print(apro_files)

for apro_file in track(apro_files, description="Processing"):
    # open the file
    (opath, filename) = os.path.split(apro_file)
    tmpfile = os.path.join(opath, "tmp.nc")
    with xr.open_dataset(apro_file, decode_times=False) as ds:

        # add altitude direction
        if "altitude" not in ds: 
            continue
        ds["altitude"] = ds["altitude"].assign_attrs({
            'positive': "up"
        })
        
        # convert time: from milliseconds to days
        if ds['time'].dtype == np.int64: 
            ds = _convert_time(ds)
        
        # convert int64 to int32
        encoding = {}
        for varname, var in ds.variables.items():
            if varname == "time": 
                continue
            if var.dtype == np.int64:
                encoding[varname] = {"dtype": np.int32, "zlib": True, "chunksizes": var.shape}
            if varname in ["extinction", "clouds_bases", "clouds_peaks", "clouds_tops"]:
                encoding[varname] = {"zlib": True, "chunksizes": var.shape}

        # convert also the quality_flag's variable flag_values attribute also to NC_INT instead of NC_INT64
        ds["quality_flag"] = ds.quality_flag.assign_attrs({'flag_values': np.array([0,1,2], dtype=np.int32)})

        # write the file
        ds.to_netcdf(tmpfile, mode='w', encoding=encoding)

    shutil.move(tmpfile, apro_file)
