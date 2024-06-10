##
# @brief Horizontal operation of 2d variable using MPI Reduce
# @author Tomoro Yanase, Team SCALE
# @note how to run: e.g., $ mpirun -n 2 python mpi_xarray_spatial_operation.py 1 2

# Import libraries ##############################################
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../mod_scale'))

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import sys
from mpi4py import MPI
plt.rcParams["font.size"]=15
from mod_scale.g_file import get_xrvar # get_fpathlist
from mod_scale.g_mpi import get_mpi, get_and_check_prc, get_fpathlist_mpi, check_prcnum_mpi


# Setting ########################################################
# directory of files and the number of simulation processes for each direction (x,y)
dir1 = "./sampledata/scale-5.4.5/scale-rm/test/tutorial/real/experiment/run/"
PRC_NUM_X = 2
PRC_NUM_Y = 2

ftype = "history" 
domainlabel = "_d01"
timelabel = ""

## Value (e.g., PREC)
## 2D (spatial) + time
varname1 = "PREC"
var_scaling_const = 3600
var_unit = "(mm/h)"

# Operation (spatial) setting 
weight_type = "cell_area" # "even" , "cell_area" # weight value for 2D  (spatial) mean
weight_scaling_const = 1 # 1 , 1e9

# Get the number of analysis processes for each direction (x,y)
args = sys.argv
PRC_NUM_X_ANL = int(args[1]) # number of process in x-direction per analysis rank; e.g., 2 
PRC_NUM_Y_ANL = int(args[2]) # number of process in y-direction per analysis rank; e.g., 2 

dir_out = "./fig/"


# MPI setting and allocation ######################################
comm,size,rank = get_mpi()
PRC_NUM_X_PER_ANL,PRC_NUM_Y_PER_ANL = get_and_check_prc(PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size)
fpathlist = get_fpathlist_mpi(dir1,ftype,domainlabel,timelabel,PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size,rank)
check_prcnum_mpi(PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size,rank)
ds = get_xrvar(fpathlist)


# Actual operation ################################################
value_ = np.array(ds[varname1].values)

# 2D spatial operation
if weight_type=="even":
    weight_ = np.ones_like(value_)
if weight_type=="cell_area":
    weight_ = np.array(ds[weight_type].values)[np.newaxis,:,:]
    weight_ = np.tile( weight_, (value_.shape[0],1,1) )
#
weight_ = weight_ / weight_scaling_const

# Weight (e.g., cell_area); sum in a single process
weight_sum_ = np.array( np.sum( weight_, axis=(1,2)), 'd') # retain time axis

# Weighted value; sum in a single process
weighted_value_ = ( value_ * weight_ )
weighted_value_sum_ = np.array( np.sum( weighted_value_, axis=(1,2) ), 'd') # retain time axis

print(f"Rank: {rank}, weighted_value_sum_, weight_sum_ =", weighted_value_sum_, weight_sum_)

# Initialize the np arrays that will store the results:
weighted_value_sum = np.array(np.zeros(weighted_value_.shape[0]),'d') # time series values
weight_sum         = np.array(np.zeros(weight_sum_.shape[0]),'d')     # time series values

# Perform the reductions
comm.Reduce(weighted_value_sum_, weighted_value_sum, op=MPI.SUM, root=0)
comm.Reduce(weight_sum_, weight_sum, op=MPI.SUM, root=0)

# Operation in a rank
value_max_ = np.array( np.max( value_, axis=(1,2) ), 'd') # retain time axis
value_min_ = np.array( np.min( value_, axis=(1,2) ), 'd') # retain time axis

# Initialize the np arrays that will store the results:
value_max         = np.array( np.zeros(value_max_.shape[0]), 'd') # time series values
value_min         = np.array( np.zeros(value_min_.shape[0]), 'd') # time series values

# Perform the reductions
comm.Reduce(value_max_, value_max, op=MPI.MAX, root=0)
comm.Reduce(value_min_, value_min, op=MPI.MIN, root=0)


# Plot figure in root rank ################################################
if rank == 0:

    time1 = ds["time"].values

    # mean plot
    print(f"Rank: {rank} weighted_value_sum, weight_sum=",  weighted_value_sum, weight_sum)
    print(" weighted_value_sum / weight_sum = ", weighted_value_sum/weight_sum)
    print(" weighted_value_sum.sum() / weight_sum.sum() = ", weighted_value_sum.sum()/weight_sum.sum())
    fig,ax=plt.subplots()
    ax.plot(time1/3600,weighted_value_sum/weight_sum*var_scaling_const,marker="o")
    ax.grid()
    ax.set_xlabel("time (h)")
    ax.set_ylabel(f"{var_unit}")
    ax.set_title(f"cell_area weighted-average of {varname1}")
    fig.tight_layout()
    fig.savefig(dir_out + f"mpi_xarray_weighted-mean_{varname1}.png")
    plt.close("all")

    # max plot
    print(f"Rank: {rank} value_max=",  value_max)
    fig,ax=plt.subplots()
    ax.plot(time1/3600,value_max*var_scaling_const,marker="o")
    ax.grid()
    ax.set_xlabel("time (h)")
    ax.set_ylabel(f"{var_unit}")
    ax.set_title(f"max {varname1}")
    fig.tight_layout()
    fig.savefig(dir_out + f"mpi_xarray_max_{varname1}.png")
    plt.close("all")

    # min plot
    print(f"Rank: {rank} value_min=",  value_min)
    fig,ax=plt.subplots()
    ax.plot(time1/3600,value_min*var_scaling_const,marker="o")
    ax.grid()
    ax.set_xlabel("time (h)")
    ax.set_ylabel(f"{var_unit}")
    ax.set_title(f"min {varname1}")
    fig.tight_layout()
    fig.savefig(dir_out + f"mpi_xarray_min_{varname1}.png")
    plt.close("all")

