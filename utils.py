def _convert_time(ds):
    ds['time'] = (ds['time'] / (1000 * 60 * 60 * 24) )
    ds["time"].attrs['units'] = 'days since 1970-01-01T00:00:00'
    return ds