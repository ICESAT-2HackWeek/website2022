#!/usr/bin/env python
u"""
ATL06_to_dataframe.py (03/2022)
Read ICESat-2 ATL06 (Land Ice Along-Track Height Product) data files
    derived from https://github.com/tsutterley/read-ICESat-2/

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
    h5py: Python interface for Hierarchal Data Format 5 (HDF5)
        https://www.h5py.org/
    geopandas: Python tools for geographic data
        http://geopandas.readthedocs.io/
"""
from __future__ import print_function

import geopandas as gpd
import h5py
import io
import logging
import numpy as np
import os
import re

# default beams to read from ATL06
DEFAULT_BEAMS = ['gt1l','gt1r','gt2l','gt2r','gt3l','gt3r']
# default groups to read from ATL06
DEFAULT_GROUPS = []
DEFAULT_GROUPS.append('bias_correction')
DEFAULT_GROUPS.append('dem')
DEFAULT_GROUPS.append('fit_statistics')
DEFAULT_GROUPS.append('geophysical')
DEFAULT_GROUPS.append('ground_track')

# PURPOSE: read ICESat-2 ATL06 HDF5 data files
def ATL06_to_dataframe(FILENAME,
   beams=DEFAULT_BEAMS,
   groups=DEFAULT_GROUPS,
   **kwargs):
    """
    Reads ICESat-2 ATL06 (Land Ice Along-Track Height Product) data files

    Arguments
    ---------
    FILENAME: full path to ATL06 file

    Keyword Arguments
    -----------------
    beams: ATLAS beam groups to read
    groups: HDF5 groups to read
    crs: Coordinate Reference System for dataframe
    
    Returns
    -------
    gdf: geodataframe with ATL06 variables
    """
    # set default EPSG
    kwargs.setdefault('crs','EPSG:4326')
    # Open the HDF5 file for reading
    if isinstance(FILENAME, io.IOBase):
        fileID = h5py.File(FILENAME, 'r')
    else:
        fileID = h5py.File(os.path.expanduser(FILENAME), 'r')

    # Output HDF5 file information
    logging.info(fileID.filename)
    logging.info(list(fileID.keys()))

    # output GeoDataFrame for ICESat-2 ATL06 variables
    gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy([],[]), crs=kwargs['crs'])

    # read each input beam within the file
    IS2_atl06_beams = []
    for gtx in [k for k in fileID.keys() if re.match(r'gt\d[lr]',k) and k in beams]:
        # check if subsetted beam contains land ice data
        try:
            fileID[gtx]['land_ice_segments']['segment_id']
        except KeyError:
            pass
        else:
            IS2_atl06_beams.append(gtx)

    # read each input beam within the file
    for gtx in IS2_atl06_beams:
        # get each HDF5 variable in ICESat-2 land_ice_segments Group
        columns = {}
        for key,val in fileID[gtx]['land_ice_segments'].items():
            if isinstance(val, h5py.Dataset):
                if val.attrs.get('_FillValue'):
                    columns[key] = val[:].astype('f')
                    columns[key][val[:] == val.fillvalue] = np.nan
                else:
                    columns[key] = val[:]
            elif isinstance(val, h5py.Group) and (val.name.split('/')[-1] in groups):
                for k,v in val.items():
                    if v.attrs.get('_FillValue'):
                        columns[k] = v[:].astype('f')
                        columns[k][v[:] == v.fillvalue] = np.nan
                    else:
                        columns[k] = v[:]
        # number of segments
        n_seg = fileID[gtx]['land_ice_segments']['h_li'].size
        # fill value
        # generate derived variables
        columns['rgt'] = np.full((n_seg),fileID['orbit_info']['rgt'][0])
        columns['cycle_number'] = np.full((n_seg),fileID['orbit_info']['cycle_number'][0])
        BP,LR = re.findall(r'gt(\d)([lr])',gtx).pop()
        columns['BP'] = np.full((n_seg),int(BP))
        columns['LR'] = [LR]*n_seg
        beam_type = fileID[gtx].attrs['atlas_beam_type'].decode('utf-8')
        columns['beam_type'] = [beam_type]*n_seg
        columns['spot'] = np.full((n_seg),fileID[gtx].attrs['atlas_spot_number'])
        # convert from dictionary to geodataframe
        delta_time = (columns['delta_time']*1e9).astype('timedelta64[ns]')
        atlas_sdp_epoch = np.datetime64('2018-01-01T00:00:00Z')
        columns['time'] = gpd.pd.to_datetime(atlas_sdp_epoch + delta_time)
        # generate geometry column
        geometry = gpd.points_from_xy(columns['longitude'], columns['latitude'])
        del columns['longitude']
        del columns['latitude']
        # create Pandas DataFrame object
        df = gpd.pd.DataFrame(columns)
        # append to GeoDataFrame
        gdf = gdf.append(gpd.GeoDataFrame(df, geometry=geometry, crs=kwargs['crs']))

    # Closing the HDF5 file
    fileID.close()

    # Return the geodataframe
    return gdf
