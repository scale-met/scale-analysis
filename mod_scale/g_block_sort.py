##
# @brief 
# @author Tomoro Yanase, Team SCALE
# @note 
import numpy as np

def get_key2d(xrvar,key2dname,blct,blcy,blcx):
    cell_area = xrvar["cell_area"].data
    key2d0 = xrvar[key2dname].data
    tsize = key2d0.shape[0]
    ysize = key2d0.shape[1]
    xsize = key2d0.shape[2]
    #
    weights = np.tile(cell_area[np.newaxis,:,:],(tsize,1,1))
    weights_reshaped = np.reshape(weights,(int(tsize/blct),blct,int(ysize/blcy),blcy,int(xsize/blcx),blcx))

    # block-average by reshape
    key2d0 = np.reshape(
        np.average(
            np.reshape(key2d0,(int(tsize/blct),blct,int(ysize/blcy),blcy,int(xsize/blcx),blcx))
            ,axis=(1,3,5)
            ,weights=weights_reshaped)
        ,(int(tsize/blct),-1)
        )
    # indexing
    index = np.argsort(key2d0,axis=1)
    key2d0 = np.array([key2d0[i,index[i,:]] for i in range(index.shape[0])])

    weights_sum = np.reshape(
        np.sum(
            weights_reshaped,
            axis=(1,3,5)),
        (int(tsize/blct),-1)
        )
    weights_sum_sorted = np.array([weights_sum[i,index[i,:]] for i in range(index.shape[0])])
    return index,key2d0,weights_sum_sorted

def get_var2d_sorted_bykey2d(xrvar,var2dname,blct,blcy,blcx,index):
    cell_area = xrvar["cell_area"].data
    var2d = xrvar[var2dname].data
    tsize = var2d.shape[0]
    ysize = var2d.shape[1]
    xsize = var2d.shape[2]
    #
    weights = np.tile(cell_area[np.newaxis,:,:],(tsize,1,1))
    weights_reshaped = np.reshape(weights,(int(tsize/blct),blct,int(ysize/blcy),blcy,int(xsize/blcx),blcx))
    var2d_reshaped = np.reshape(var2d,(int(tsize/blct),blct,int(ysize/blcy),blcy,int(xsize/blcx),blcx))
    #
    var2d_avg = np.average(var2d_reshaped,weights=weights_reshaped, axis=(1,3,5))
    var2d_reshaped = np.reshape(var2d_avg,(int(tsize/blct),-1))
    var2d_sorted = np.array([var2d_reshaped[i,index[i,:]] for i in range(index.shape[0])])
    return var2d_sorted

def get_var3d_sorted_bykey2d(xrvar,var3dname,blct,blcy,blcx,index):
    if var3dname=="RHOW":
        var3d = (xrvar["DENS"].data)*(xrvar["W"].data)
    else:
        var3d = xrvar[var3dname].data
    cell_area = xrvar["cell_area"].data
    tsize = var3d.shape[0]
    zsize = var3d.shape[1]
    ysize = var3d.shape[2]
    xsize = var3d.shape[3]
    # 
    weights = np.tile(cell_area[np.newaxis,np.newaxis,:,:],(tsize,zsize,1,1))
    weights_reshaped = np.reshape(weights,(int(tsize/blct),blct,int(zsize),int(ysize/blcy),blcy,int(xsize/blcx),blcx))
    #
    var3d_reshaped = np.reshape(
        np.average(
            np.reshape(var3d,(int(tsize/blct),blct,int(zsize),int(ysize/blcy),blcy,int(xsize/blcx),blcx))
            ,axis=(1,4,6)
            ,weights=weights_reshaped)
        ,(int(tsize/blct),int(zsize),-1)
        )
    var3d_sorted = np.swapaxes(np.array([var3d_reshaped[i,:,index[i,:]] for i in range(index.shape[0])]),1,2)
    return var3d_sorted


def get_blcavg(xrvar,var2dname,blct,blcy,blcx):
    cell_area = xrvar["cell_area"].data
    var2d = xrvar[var2dname].data
    tsize = var2d.shape[0]
    ysize = var2d.shape[1]
    xsize = var2d.shape[2]
    #
    weights = np.tile(cell_area[np.newaxis,:,:],(tsize,1,1))
    weights_reshaped = np.reshape(weights,(int(tsize/blct),blct,int(ysize/blcy),blcy,int(xsize/blcx),blcx))
    var2d_reshaped = np.reshape(var2d,(int(tsize/blct),blct,int(ysize/blcy),blcy,int(xsize/blcx),blcx))
    #
    var2d_avg = np.average(var2d_reshaped,weights=weights_reshaped, axis=(1,3,5))
    return var2d_avg