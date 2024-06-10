##
# @brief 
# @author Tomoro Yanase, Team SCALE
# @note 

import xarray as xr

def get_fpathlist(dir1,ftype,domainlabel,timelabel,PRC_NUM_X,PRC_NUM_Y):
    return [ [ dir1 + "{0}{1}{2}.pe{3:06d}.nc".format( ftype, domainlabel, timelabel, i + j*PRC_NUM_X ) for i in range(PRC_NUM_X) ] for j in range(PRC_NUM_Y) ]

def get_xrvar(fpathlist):
    return xr.open_mfdataset(fpathlist, decode_times=False, combine="nested", concat_dim=["y","x"])

