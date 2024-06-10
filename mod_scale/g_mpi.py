
##
# @brief 
# @author Tomoro Yanase, Team SCALE
# @note 

from mpi4py import MPI # https://mpi4py.readthedocs.io/en/latest/index.html
import sys
import numpy as np
#import xarray as xr # https://docs.xarray.dev/en/stable/

def get_mpi():
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    return comm,size,rank

def get_and_check_prc(PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size):
    # Check consistency of MPI and setting
    #print("Check PRC_NUM_X_ANL and PRC_NUM_Y_ANL")
    if (PRC_NUM_X_ANL*PRC_NUM_Y_ANL)==size:
        pass
    else:
        print(f"Exit: it should (PRC_NUM_X_ANL*PRC_NUM_Y_ANL)==size, but {PRC_NUM_X_ANL*PRC_NUM_Y_ANL}!={size}")
        sys.exit()
    if (int(PRC_NUM_X)%int(PRC_NUM_X_ANL)==0) and (int(PRC_NUM_Y)%int(PRC_NUM_Y_ANL)==0):
        pass
    else:
        print(f"Exit: it should (int(PRC_NUM_X)%int(PRC_NUM_X_ANL)==0) and (int(PRC_NUM_Y)%int(PRC_NUM_Y_ANL)==0), but {int(PRC_NUM_X)%int(PRC_NUM_X_ANL)} and {int(PRC_NUM_Y)%int(PRC_NUM_Y_ANL)}")
        sys.exit()
    PRC_NUM_X_PER_ANL = int(PRC_NUM_X)//int(PRC_NUM_X_ANL)
    PRC_NUM_Y_PER_ANL = int(PRC_NUM_Y)//int(PRC_NUM_Y_ANL)
    return PRC_NUM_X_PER_ANL,PRC_NUM_Y_PER_ANL

def get_fpathlist_mpi(dir1,ftype,domainlabel,timelabel,PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size,rank):
    PRC_NUM_X_PER_ANL,PRC_NUM_Y_PER_ANL = get_and_check_prc(PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size)
    fpathlist = [ [ dir1 + "{0}{1}{2}.pe{3:06d}.nc".format(ftype,domainlabel,timelabel, i + j*PRC_NUM_X ) for i in range( PRC_NUM_X_PER_ANL*(rank%PRC_NUM_X_ANL), PRC_NUM_X_PER_ANL*(rank%PRC_NUM_X_ANL+1) )] for j in range( PRC_NUM_Y_PER_ANL*((rank)//PRC_NUM_X_ANL),PRC_NUM_Y_PER_ANL*((rank)//PRC_NUM_X_ANL + 1) ) ]
    return fpathlist

def check_prcnum_mpi(PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size,rank):
    PRC_NUM_X_PER_ANL,PRC_NUM_Y_PER_ANL = get_and_check_prc(PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size)
    PRC_NUM_ARR = np.arange(PRC_NUM_X*PRC_NUM_Y).reshape((PRC_NUM_Y,PRC_NUM_X))
    print(f"Rank:{rank}, 2d arr of prc",PRC_NUM_ARR[ PRC_NUM_Y_PER_ANL*((rank)//PRC_NUM_X_ANL):PRC_NUM_Y_PER_ANL*((rank)//PRC_NUM_X_ANL + 1), PRC_NUM_X_PER_ANL*(rank%PRC_NUM_X_ANL):PRC_NUM_X_PER_ANL*(rank%PRC_NUM_X_ANL+1)])
    return PRC_NUM_ARR[ PRC_NUM_Y_PER_ANL*((rank)//PRC_NUM_X_ANL):PRC_NUM_Y_PER_ANL*((rank)//PRC_NUM_X_ANL + 1), PRC_NUM_X_PER_ANL*(rank%PRC_NUM_X_ANL):PRC_NUM_X_PER_ANL*(rank%PRC_NUM_X_ANL+1)]

def combine_var2d_blockavg(sendbuf,recvbuf,PRC_NUM_Y_ANL,PRC_NUM_X_ANL):
    var2d_avg_combined = np.empty((sendbuf.shape[0],sendbuf.shape[1]*PRC_NUM_Y_ANL,sendbuf.shape[2]*PRC_NUM_X_ANL))
    for PRC_NUM_Y_ANL0 in range(PRC_NUM_Y_ANL):
        for PRC_NUM_X_ANL0 in range(PRC_NUM_X_ANL):
            rank0 = PRC_NUM_Y_ANL0*PRC_NUM_X_ANL + PRC_NUM_X_ANL0
            var2d_avg_combined[:,sendbuf.shape[1]*PRC_NUM_Y_ANL0:sendbuf.shape[1]*(PRC_NUM_Y_ANL0+1),sendbuf.shape[2]*PRC_NUM_X_ANL0:sendbuf.shape[2]*(PRC_NUM_X_ANL0+1)] = recvbuf[rank0,:,:,:]
    print("var2d_avg_combined.shape",var2d_avg_combined.shape)
    return var2d_avg_combined
