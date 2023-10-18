#!/usr/bin/env python

import sys,os
import math
import struct
import matplotlib.pyplot as plt
import numpy as np
import copy
import os.path
import matplotlib.dates as mdates

from netCDF4 import Dataset 
from scipy.interpolate import Rbf
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from calendar import monthrange

######################################################
# FUNCTIONS
# ####################################################
years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')

exp_name='EAS5'
fig_dir ='./'

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month
    # d1 = last year
    # d2 = first year


def dateloop(d1, d2,freq):
    if freq == 0:
      return (d1 + timedelta(days=i) for i in range((d2 - d1).days + 1))
    elif freq == 1:
      return (d1 + 7*timedelta(days=i) for i in range((d2-d1).days//7 +1))
    elif freq == 2:
      return (d1 + relativedelta(months=i) for i in range(diff_month(d2, d1) + 1))


############################################################
# END FUNCIONTS
############################################################


# mode = 0 -> hovmoller from SIMULATION
# mode = 1 -> hovmoller from ANALYSIS
mode = 1 

# In case of reanalysis choose 0 => we read also XBT
# else choose 1 => we read only ARGO
system = 1

# first and last dates of computation: 
sd=datetime(2018,1,1)
ed=datetime(2020,12,30)

# Frequency of computation:
#   0 = daily 
#   1 = weekly
#   2 = monthly
freq = 1

# Label maximum values:
max_salinity_label = 0.3 # with OBSSTAT:0.35, with OBSSTAT_SCREEN: 0.8
max_temp_label = 1.8     # with OBSSTAT:1.5, with OBSSTAT_SCREEN:2.5

# Counts the space we need depending on frequency:
if freq == 0:
   space = (ed-sd).days   
elif freq == 1:
   space = (ed-sd).days//7+1
elif freq == 2:
   space = diff_month(ed, sd)+1


# Counts the years
years_diff = int(ed.year) - int(sd.year)
years = []
for i in range(years_diff+1):
  years.append(int(sd.year)+i)

fh = Dataset('RMS_hovmoller_V1.nc', mode='r')
rmseT_masked = fh.variables["rms_temperature"][:,:]
rmseS_masked = fh.variables["rms_salinity"][:,:]
biasT_masked = fh.variables["bias_temperature"][:,:]
biasS_masked = fh.variables["bias_salinity"][:,:]
dept = fh.variables["depth"][:]
time = fh.variables["time"][:]
fh.close()

x=np.arange(0,np.size(rmseT_masked,1),1)
y=np.arange(0,np.size(rmseT_masked,0),1)
X,Y=np.meshgrid(x,y)
ncycle=np.size(rmseT_masked,0)-2
if not os.path.isdir(fig_dir):
  os.mkdir(fig_dir)

if freq == 0:
  freq_label_plot = 365
  name_plot = 'daily' 
elif freq == 1:
  freq_label_plot = 52
  name_plot = 'weekly'
elif freq == 2:
  freq_label_plot = 3
  name_plot = 'monthly'


# Temperature:
# ------------
plt.figure(figsize=(10, 5))
cmapT=plt.cm.jet
csT=plt.pcolor(Y,X,rmseT_masked,cmap=cmapT,vmin=0, vmax=max_temp_label)
plt.xlim([0,np.size(rmseT_masked,0)-2])
plt.ylim([1,np.size(rmseT_masked,1)-4])
plt.gca().invert_yaxis()
plt.xticks(np.arange(0,ncycle,13.1),['Jan-18','Apr-18','Jul-18','Oct-18','Jan-19','Apr-19','Jul-19','Oct-19','Jan-20','Apr-20','Jul-20','Oct-20'],
        rotation=45,fontsize=14)
plt.yticks(np.arange(1,80,10),dept[0::10],fontsize=14)
t_name="TEMPERATURE RMS misfits [$^\circ$C] "+exp_name
plt.ylabel("Depth [m]",fontsize=15)
cbar=plt.colorbar(csT,orientation="vertical")
cbar.ax.tick_params(labelsize=14)
cbar.set_label('Temp. RMSD [$^\circ$C]',fontsize=15)
plt.text(0,0, '(a)',
        color='black', fontsize=16,fontweight='bold')
plt.savefig(fig_dir+'/bis_T_rmse_HOVMOLLER_'+
	    name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png',bbox_inches='tight')
plt.clf()
plt.cla()
plt.close()


# BIAS ------------
plt.figure(figsize=(10, 5))
cmapT=plt.cm.bwr
csT=plt.pcolor(Y,X,biasT_masked,cmap=cmapT,vmin=-0.45, vmax=0.45)
plt.xlim([0,np.size(biasT_masked,0)-2])
plt.ylim([1,np.size(biasT_masked,1)-4])
plt.gca().invert_yaxis()
plt.xticks(np.arange(0,ncycle,13.1),['Jan-18','Apr-18','Jul-18','Oct-18','Jan-19','Apr-19','Jul-19','Oct-19','Jan-20','Apr-20','Jul-20','Oct-20'],
        rotation=45,fontsize=14)
plt.yticks(np.arange(1,80,10),dept[0::10],fontsize=14)
t_name="TEMPERATURE Bias [$^\circ$C] "+exp_name
plt.ylabel("Depth [m]",fontsize=15)
cbar=plt.colorbar(csT,orientation="vertical")
cbar.ax.tick_params(labelsize=14)
cbar.set_label('Temp. BIAS [$^\circ$C]',fontsize=15)
plt.text(0,0, '(c)',
        color='black', fontsize=16,fontweight='bold')
plt.savefig(fig_dir+'/bis_T_bias_HOVMOLLER_'+
            name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png',bbox_inches='tight')

plt.clf()
plt.cla()
plt.close()

# Salinity:
# ---------
plt.figure(figsize=(10, 5))
cmapS=plt.cm.jet
csS=plt.pcolor(Y,X,rmseS_masked,cmap=cmapS,vmin=0, vmax=max_salinity_label)
plt.xlim([0,np.size(rmseT_masked,0)-2])
plt.ylim([1,np.size(rmseT_masked,1)-4])
plt.gca().invert_yaxis()
plt.xticks(np.arange(0,ncycle,13.1),['Jan-18','Apr-18','Jul-18','Oct-18','Jan-19','Apr-19','Jul-19','Oct-19','Jan-20','Apr-20','Jul-20','Oct-20'],
        rotation=45,fontsize=14)
plt.yticks(np.arange(1,80,10),dept[0::10],fontsize=14)
s_name="SALINITY RMS misfits [PSU] "+exp_name
plt.ylabel("Depth [m]",fontsize=15)
cbar=plt.colorbar(csS,orientation="vertical")
cbar.ax.tick_params(labelsize=14)
cbar.set_label('Sal. RMSD [PSU]',fontsize=15)
plt.text(0,0, '(b)',
        color='black', fontsize=16,fontweight='bold')
plt.savefig(fig_dir+'/bis_S_rmse_HOVMOLLER_'+
            name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png',bbox_inches='tight')
plt.clf()
plt.cla()
plt.close()

# BIAS ---------
plt.figure(figsize=(10, 5))
cmapS=plt.cm.bwr
csS=plt.pcolor(Y,X,biasS_masked,cmap=cmapS,vmin=-0.1, vmax=0.1)
plt.xlim([0,np.size(biasS_masked,0)-2])
plt.ylim([1,np.size(biasS_masked,1)-4])
plt.gca().invert_yaxis()
plt.xticks(np.arange(0,ncycle,13.1),['Jan-18','Apr-18','Jul-18','Oct-18','Jan-19','Apr-19','Jul-19','Oct-19','Jan-20','Apr-20','Jul-20','Oct-20'],
        rotation=45,fontsize=14)
plt.yticks(np.arange(1,80,10),dept[0::10],fontsize=14)
s_name="SALINITY BIAS [PSU] "+exp_name
plt.ylabel("Depth [m]",fontsize=15)
cbar=plt.colorbar(csS,orientation="vertical")
cbar.ax.tick_params(labelsize=14)
cbar.set_label('Sal. BIAS [PSU]',fontsize=15)
plt.text(0,0, '(d)',
        color='black', fontsize=16,fontweight='bold')
plt.savefig(fig_dir+'/bis_S_bias_HOVMOLLER_'+
            name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png',bbox_inches='tight')

plt.clf()
plt.cla()
plt.close()


