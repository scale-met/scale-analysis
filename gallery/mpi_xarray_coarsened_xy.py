##
# @brief Coarsened plot of 2d variable using MPI Gather
# @author Tomoro Yanase, Team SCALE
# @note how to run: e.g., $ mpirun -n 2 python mpi_xarray_coarsened_xy.py 1 2

# Import libraries ######################################################################
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../mod_scale'))

import numpy as np
#import xarray as xr
import matplotlib.pyplot as plt
import sys
from mpi4py import MPI
plt.rcParams["font.size"]=15

from mod_scale.g_file import get_xrvar, get_fpathlist
from mod_scale_mpi import get_mpi, get_and_check_prc, get_fpathlist_mpi, check_prcnum_mpi, combine_var2d_blockavg
from mod_scale_block_sort import get_blcavg


# Setting ################################################################################
# directory of files and the number of simulation processes for each direction (x,y)
dir1 = "./sampledata/scale-5.4.5/scale-rm/test/tutorial/real/experiment/run/"
PRC_NUM_X = 2 # 2 , 6
PRC_NUM_Y = 2 # 2 , 6

ftype = "history" 
domainlabel = "_d01"
timelabel = ""

## Value (e.g., PREC)
## 2D (spatial) + time
varname1 = "T2"
varunit1 = "(K)"
varfact1 = 1
varlevels1 = np.linspace(265,305,41)
varcmap1 = "jet"
#varname1 = "PREC"
#varunit1 = r"$\mathrm{(mm/h)}$"
#varfact1 = 3600
#varlevels1 = np.linspace(5,40,8)
#varcmap1 = "rainbow"

# Number of space-time points for a block-average
blct = 1
blcy = 15
blcx = 15

# Get the number of analysis processes for each direction (x,y)
args = sys.argv
PRC_NUM_X_ANL = int(args[1]) # number of process in x-direction per analysis rank; e.g., 2 
PRC_NUM_Y_ANL = int(args[2]) # number of process in y-direction per analysis rank; e.g., 2 

dir_out = "./fig/"
#horaxis = "XY"
horaxis = "LATLON"
withmap = True
lonticks=np.arange(80,180+1,10)
latticks=np.arange(10,60+1,10)
slon = 120
elon = 150
slat = 25
elat = 45

savefig = True


# MPI setting and allocation ##################################################################
comm,size,rank = get_mpi()
PRC_NUM_X_PER_ANL,PRC_NUM_Y_PER_ANL = get_and_check_prc(PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size)

# file path list for each MPI process
fpathlist = get_fpathlist_mpi(dir1,ftype,domainlabel,timelabel,PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size,rank)
PRC_NUM_ARR0 = check_prcnum_mpi(PRC_NUM_X,PRC_NUM_Y,PRC_NUM_X_ANL,PRC_NUM_Y_ANL,size,rank)
xrvar = get_xrvar(fpathlist)

var2d_avg = get_blcavg(xrvar,varname1,blct,blcy,blcx)
sendbuf = np.array(var2d_avg,"d")
#print('Rank: ',rank, ', sendbuf: ',sendbuf)

recvbuf = None
if rank == 0:
    recvbuf = np.array(np.tile(np.empty_like(sendbuf),(size,1,1,1)), dtype='d')  

comm.Gather(sendbuf, recvbuf, root=0)


# Plot at zero-rank ###########################################################################
if rank == 0:
    print('Rank: ',rank, ', recvbuf received: ',recvbuf)
    var2d_avg_combined = combine_var2d_blockavg(sendbuf,recvbuf,PRC_NUM_Y_ANL,PRC_NUM_X_ANL)

    fpathlist =  get_fpathlist(dir1,"history",domainlabel,timelabel,PRC_NUM_X,PRC_NUM_Y)
    xrvar = get_xrvar(fpathlist)
    time = xrvar.coords["time"]
    tsize = len(time)

    for t in range(int(tsize/blct)):
        print("t",t)
        tlabel = f"{t*blct:04d}-{(t+1)*blct-1:04d}"

        if horaxis=="LATLON":
            lon = xrvar.coords["lon"]
            lat = xrvar.coords["lat"]
            if withmap:
                import cartopy.crs as ccrs
                from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
                fig = plt.figure(figsize=(8,5))
                ax = fig.add_subplot(111,projection=ccrs.PlateCarree())
                ax.coastlines('10m',color='gray')
                ax.set_xticks(lonticks, crs=ccrs.PlateCarree())
                ax.set_yticks(latticks, crs=ccrs.PlateCarree())
                ax.xaxis.set_major_formatter(LongitudeFormatter())
                ax.yaxis.set_major_formatter(LatitudeFormatter())
                ax.gridlines(xlocs=lonticks, ylocs=latticks)
            else:
                fig,ax=plt.subplots(figsize=(8,5))
            cax = ax.contourf(lon[blcy//2::blcy,blcx//2::blcx],lat[blcy//2::blcy,blcx//2::blcx],varfact1*var2d_avg_combined[t,:,:],levels=varlevels1,cmap=varcmap1)
            ax.set_xlabel("lon")
            ax.set_ylabel("lat")
            ax.set_xlim(slon,elon)
            ax.set_ylim(slat,elat)
            figtitle = f"mpi_xarray_coarsened_ll_{varname1}_blct{blct:04d}blcy{blcy:04d}blcx{blcx:04d}_t{tlabel}.png"

        if horaxis=="XY":
            fig,ax=plt.subplots(figsize=(8,5))
            x = xrvar.coords["x"]
            y = xrvar.coords["y"]
            cax = ax.contourf(1e-3*x[blcx//2::blcx],1e-3*y[blcy//2::blcy],varfact1*var2d_avg_combined[t,:,:],levels=varlevels1,cmap=varcmap1)
            ax.set_xlabel("x [km]")
            ax.set_ylabel("y [km]")
            figtitle = f"mpi_xarray_coarsened_xy_{varname1}_blct{blct:04d}blcy{blcy:04d}blcx{blcx:04d}_t{tlabel}.png"

        ax.set_aspect("equal")
        ax.set_title(f"{varname1}_t{tlabel}")
        cbar = plt.colorbar(cax,ax=ax)
        cbar.set_label(varunit1)
        fig.tight_layout()
        if savefig:
            fig.savefig(dir_out + figtitle)
            plt.close("all")

