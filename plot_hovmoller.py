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

############################################################
# INSTRUCTIONS
############################################################

# To run the script: ./ hovmoller_obsstat.py
# Indata folder: 
  # place the OBSSTAT files of one year in a folder 
  # named  yy+'year', eg. yy2016
  # and provide its location where specified 
  # (In_dir variable)
# The script produces 2 plots, one for T and one for S
# For monthly frequency plots set the starting date 
  # from the first day of the first month you want to consider
  # even if there are no OBSSTAT files for this date.

#####################################################
# USER CHOICES:
####################################################

# fname = 0 -> to read OBSSTAT files
# fname = 1 -> to read OBSSTAT_SCREEN files
fname = 0 

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

m_nc=Dataset('mesh_mask.nc')

if fname == 0:
  source = 'obsstat'
elif fname == 1:
  source = 'obsstat_screen'

if mode == 0:
  run = 'SIMU'
elif mode == 1:
  run = 'REA'

In_dir='/DATA/EAS5/yy2017'
exp_name='EAS5'
fig_dir ='./FIGURE/'

###########################################################
# AUTOMATIC
##########################################################

dvals=m_nc.variables['gdept_0'][-1,0:74,-1,-1]
dept=np.around(np.array(dvals[0:74]))
dept=dept.astype(int)

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

# We allocate space:
   # (since we want some empty space at the end of the diagram we add e +2)
countT=np.full((space+2,74),0,dtype=float)
countS=np.full((space+2,74),0,dtype=float)
rmseS=np.full((space+2,74),0,dtype=float)
rmseT=np.full((space+2,74),0,dtype=float)
biasS=np.full((space+2,74),0,dtype=float)
biasT=np.full((space+2,74),0,dtype=float)


# ncycle = counts the number of cycle 
ncycle = 0
#--------------------------------------------
# LOOP CYCLE
#---------------------------------------------
for d in dateloop(sd, ed,freq):
 
 # ndays = determine how many days contains each cycle
 print ('')
 print ('cycle number: ', ncycle)
 print ('')
 print ('FIRST LOOP DATE: ',d.strftime('%Y.%m.%d'))
 today = d
 delta = timedelta(days=1)
 if freq == 0:
   end_date = today + timedelta(days=1)
   #ndays = 1
 elif freq == 1:
   end_date = today + timedelta(days=7)
   if end_date > ed:
      end_date = ed + timedelta(days=1)
   #ndays = 7
 elif freq == 2:
   end_date = today + relativedelta(months=1)
   if end_date > ed:
      end_date = ed + timedelta(days=1)
   #ndays = monthrange(today.year, today.month)[1]
 #print 'number of days for this cycle: ',ndays


 print ('LAST LOOP DATE (excluded): ',end_date.strftime('%Y.%m.%d'))
 count_days = 0 #useless 
 while today < end_date:
    print ('working date: ',today.strftime("%Y-%m-%d")) 
	# date to be read and computed for each cycle!!!

    yy = today.year
    if fname == 0:
      file_name = 'OBSSTAT.NC.'+today.strftime("%Y%m%d")
    elif fname == 1:
      file_name = 'OBSSTAT_SCREEN.NC.'+today.strftime("%Y%m%d")+'00'

    #--------------------------------------------------
    #       READING OBSSTAT FILE
    #--------------------------------------------------
#    fileo= In_dir + str(yy) + '/' +file_name
    fileo= In_dir + '/' +file_name
   
    print (fileo)

    if not os.path.isfile(fileo):
      print (fileo, '    ...FILE NOT PRESENT')
    if os.path.isfile(fileo) and os.path.getsize(fileo)==566194196:
        print ('    ...NO OBS IN THIS DAY')

    if os.path.isfile(fileo) and  os.path.getsize(fileo)!=566194196:
      # in days of reanalysis where there are no obs, OBSSTAT files
      # are copies of empty ANINCR files => we discard them!	
      OMG = Dataset(fileo).variables["OMG"]
      PARAM = Dataset(fileo).variables["PARAM"]
      DEPTH = Dataset(fileo).variables["DEPTH"]
      LON = Dataset(fileo).variables["LON"]
      LAT = Dataset(fileo).variables["LAT"]
      TYPE = np.array(Dataset(fileo).variables["TYPE"])
      VALUE = Dataset(fileo).variables["VALUE"]
      TIME = Dataset(fileo).variables["TIME"]

      # Select sla(21)-argo(831)-xbt(401)
      sla_index = []
      type_list = TYPE.tolist()
      for i, j in enumerate(type_list):
        if j == 21:
          sla_index.append(i)

      argo_index = []
      type_list = TYPE.tolist()
      for i, j in enumerate(type_list):
         if j==831:
           argo_index.append(i)

      xbt_index = []
      type_list = TYPE.tolist()
      for i, j in enumerate(type_list):
          if j==401:
            xbt_index.append(i)

      glider_index = []
      type_list = TYPE.tolist()
      for i, j in enumerate(type_list):
          if j == 820:
            glider_index.append(i)

      #----------------------------------------------- 
      ### SELECT T,S PROFILES (ARGO, CTD)
      #----------------------------------------------

      if argo_index == []:
        print ('   ...NO ARGO on '+ str(today))
      else:
        AA=np.empty(shape=[7,np.size(argo_index,0)])
        #AA=np.empty(shape=[6,np.size(argo_index,0)])

        AA[0] = TIME[argo_index] # time
        AA[1] = LON[argo_index]# lon
        AA[2] = LAT[argo_index] # lat
        AA[3] = PARAM[argo_index] # par
        AA[4] = DEPTH[argo_index] # depth
        AA[5] = VALUE[argo_index] - OMG[argo_index] # back
        AA[6] = VALUE[argo_index] # obs_val

        #AA[0] = TIME[argo_index] # time
        #AA[1] = LON[argo_index]# lon
        #AA[2] = LAT[argo_index] # lat
        #AA[3] = PARAM[argo_index] # par
        #AA[4] = DEPTH[argo_index] # depth
        #AA[5] = OMG[argo_index] # misfit

        while np.size(AA,1) != 0:
          for p in range(1,3):

            if np.size(AA,1) != 0:
              if np.size(AA) == 7:
              #if np.size(AA) == 6:
                # TIME LON LAT PAR
                index = np.array(np.where((AA[0] == AA[0,:]) 
		  & (AA[1] == AA[1,:]) & (AA[2] == AA[2,:]) 
		  & (p == AA[3] )))
              elif np.size(AA) != 0:
                index = np.array(np.where((AA[0,1] == AA[0,:]) 
		  & (AA[1,1] == AA[1,:]) & (AA[2,1] == AA[2,:]) 
		  & (p == AA[3,:] )))

            # Se non ci sono profili che corrispondono alla selezione in base a tempo e posizione
            if np.size(index,1) == 1:
              AA=np.delete(AA,index,1)
              index=[]

            if np.size(index) > 0 :
              if np.size(AA) != 0:
                #print AA[1,index[0][1]]
                if AA[1,index[0][1]] <= -5.9375:
                  AA=np.delete(AA,index,1)
                  index=[]
                  continue
                else:
                  obsint=np.interp(dvals,np.reshape(AA[4,index],
                  np.size(index)),np.reshape(AA[6,index],
                  np.size(index)),right=0,left=0)
                  bckint=np.interp(dvals,np.reshape(AA[4,index],
                  np.size(index)),np.reshape(AA[5,index],
                  np.size(index)),right=0,left=0)
                  #omgint=np.interp(dvals,np.reshape(AA[4,index],
                  #     np.size(index)),np.reshape(AA[5,index],
                  #     np.size(index)),right=0,left=0)
                  AA=np.delete(AA,index,1)
                  if p == 1:
                    rmseS[ncycle,:]=(rmseS[ncycle,:]+(obsint-bckint)**2.)
                    biasS[ncycle,:]=(biasS[ncycle,:]+(-obsint+bckint))
		  	# old Claudia's computation
                    nobs=(obsint-bckint)!=0
            	    #nobs=omgint!=0
                    countS[ncycle,:]=(np.array(countS[ncycle,:]+nobs.astype(int)))
                    del nobs
                  else:
                    rmseT[ncycle,:]=(rmseT[ncycle,:]+(obsint-bckint)**2.)
                    biasT[ncycle,:]=(biasT[ncycle,:]+(-obsint+bckint))
		  	# old Claudia's computation
                    nobs=(obsint-bckint)!=0
            	      #nobs=omgint-omgint!=0
                    countT[ncycle,:]=(np.array(countT[ncycle,:]+nobs.astype(int)))
                    del nobs



      #----------------------------------------- 
      # SELECT T PROFILES (XBT)
      #----------------------------------------

      if not system == 1:
        if xbt_index == []:
          print ('   ...NO XBT on '+ str(today))
        else:
          AA=np.empty(shape=[7,np.size(xbt_index,0)])
          #AA=np.empty(shape=[6,np.size(xbt_index,0)])

          AA[0] = TIME[xbt_index] # time
          AA[1] = LON[xbt_index]# lon
          AA[2] = LAT[xbt_index] # lat
          AA[3] = PARAM[xbt_index] # par
          AA[4] = DEPTH[xbt_index] # depth
          AA[5] = VALUE[xbt_index] - OMG[xbt_index] # back
          AA[6] = VALUE[xbt_index] # obs_val

          #AA[0] = TIME[xbt_index] # time
          #AA[1] = LON[xbt_index]# lon
          #AA[2] = LAT[xbt_index] # lat
          #AA[3] = PARAM[xbt_index] # par
          #AA[4] = DEPTH[xbt_index] # depth
          #AA[5] = OMG[xbt_index] # misfit


          while np.size(AA,1) != 0:

            if np.size(AA,1) != 0:
              if np.size(AA) == 7:
              #if np.size(AA) == 6:
                # TIME LON LAT
                index = np.array(np.where((AA[0] == AA[0,:]) 
		  & (AA[1] == AA[1,:]) & (AA[2] == AA[2,:])))
              elif np.size(AA) != 0:
                index = np.array(np.where((AA[0,1] == AA[0,:]) 
		  & (AA[1,1] == AA[1,:]) & (AA[2,1] == AA[2,:]) ))

            # Se non ci sono profili che corrispondono alla selezione in base a tempo e posizione
            if np.size(index,1) == 1:
              AA=np.delete(AA,index,1)
              index=[]

            if np.size(index) > 0 :
              if np.size(AA) != 0:
                #print AA[1,index[0][1]]
                if AA[1,index[0][1]] <= -5.9375:
                  AA=np.delete(AA,index,1)
                  index=[]
                  continue
                else:
                  obsint=np.interp(dvals,np.reshape(AA[4,index],
		  	np.size(index)),np.reshape(AA[6,index],
		  	np.size(index)),right=0,left=0)
                  bckint=np.interp(dvals,np.reshape(AA[4,index],
		  	np.size(index)),np.reshape(AA[5,index],
		  	np.size(index)),right=0,left=0)
                  #omgint=np.interp(dvals,np.reshape(AA[4,index],
                  #     np.size(index)),np.reshape(AA[5,index],
                  #     np.size(index)),right=0,left=0)
                  AA=np.delete(AA,index,1)
                  rmseT[ncycle,:]=(rmseT[ncycle,:]+(obsint-bckint)**2.)
                  biasT[ncycle,:]=(biasT[ncycle,:]+(-obsint+bckint))
		  	# old Claudia's computation
                  nobs=(obsint-bckint)!=0
                  #nobs=omgint!=0
                  countT[ncycle,:]=(np.array(countT[ncycle,:]+nobs.astype(int)))
                  del nobs





    # end of a day of compuatation
    today += delta
    count_days +=1
 # ------ end of a frequency cycle
 ncycle +=1    


rmseT[countT==0]=np.nan
biasT[countT==0]=np.nan
countT[countT==0]=np.nan
rmseT=np.sqrt(rmseT/countT)
biasT=(biasT/countT)
countT[-1]=np.nan
#rmseT=(rmseT/countT)
	# old Claudia's computation
rmseT_masked = np.ma.masked_where(np.isnan(rmseT),rmseT)
biasT_masked = np.ma.masked_where(np.isnan(biasT),biasT)
countT_masked = np.ma.masked_where(np.isnan(countT),countT)


rmseS[countS==0]=np.nan
biasS[countS==0]=np.nan
countS[countS==0]=np.nan
rmseS=np.sqrt(rmseS/countS)
biasS=(biasS/countS)
countS[-1]=np.nan
#rmseS=(rmseS/countS)
	# old Claudia's computation
rmseS_masked = np.ma.masked_where(np.isnan(rmseS),rmseS)
biasS_masked = np.ma.masked_where(np.isnan(biasS),biasS)
countS_masked = np.ma.masked_where(np.isnan(countS),countS)



x=np.arange(0,np.size(rmseT,1),1)
y=np.arange(0,np.size(rmseT,0),1)
X,Y=np.meshgrid(x,y)

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
plt.xlim([0,np.size(rmseT,0)-2])
plt.ylim([1,np.size(rmseT,1)-4])
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
plt.savefig(fig_dir+'/T_rmse_HOVMOLLER_'+
	    name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png',bbox_inches='tight')
plt.clf()
plt.cla()
plt.close()


# BIAS ------------
plt.figure(figsize=(10, 5))
cmapT=plt.cm.bwr
csT=plt.pcolor(Y,X,biasT_masked,cmap=cmapT,vmin=-0.45, vmax=0.45)
plt.xlim([0,np.size(biasT,0)-2])
plt.ylim([1,np.size(biasT,1)-4])
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
plt.savefig(fig_dir+'/T_bias_HOVMOLLER_'+
            name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png',bbox_inches='tight')

plt.clf()
plt.cla()
plt.close()

# Salinity:
# ---------
plt.figure(figsize=(10, 5))
cmapS=plt.cm.jet
csS=plt.pcolor(Y,X,rmseS_masked,cmap=cmapS,vmin=0, vmax=max_salinity_label)
plt.xlim([0,np.size(rmseT,0)-2])
plt.ylim([1,np.size(rmseT,1)-4])
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
plt.savefig(fig_dir+'/S_rmse_HOVMOLLER_'+
            name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png',bbox_inches='tight')
plt.clf()
plt.cla()
plt.close()

# BIAS ---------
plt.figure(figsize=(10, 5))
cmapS=plt.cm.bwr
csS=plt.pcolor(Y,X,biasS_masked,cmap=cmapS,vmin=-0.1, vmax=0.1)
plt.xlim([0,np.size(biasS,0)-2])
plt.ylim([1,np.size(biasS,1)-4])
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
plt.savefig(fig_dir+'/S_bias_HOVMOLLER_'+
            name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png',bbox_inches='tight')

plt.clf()
plt.cla()
plt.close()





## Number of data for salinity:
## ----------------------------
#cmapSdata=plt.cm.jet
##levels=np.arange(0,200,20)
##csSdata=plt.contourf(Y,X,countS,cmap=cmapSdata,levels=levels,extend='both')
#csSdata=plt.pcolor(Y,X,countS_masked,cmap=cmapSdata,vmin=0, vmax=200)
##plt.xlim([0,np.size(rmseT,0)-15])
#plt.xlim([0,np.size(rmseT,0)-2])
#plt.ylim([0,np.size(rmseT,1)-4])
#plt.gca().invert_yaxis()
#plt.xticks(np.arange(0,ncycle,freq_label_plot),years[0::1],
#        rotation=45,fontsize=10,fontweight='bold')
#plt.yticks(np.arange(1,80,10),dept[0::10],fontsize=10,fontweight='bold')
#sdata_name="SALINITY n. DATA "+exp_name 
#plt.title(sdata_name,fontsize=12,fontweight='bold')
#plt.xlabel("time",fontsize=10,fontweight='bold')
#plt.ylabel("depth",fontsize=10,fontweight='bold')
#cbar=plt.colorbar(csSdata,orientation="vertical")
#plt.savefig(fig_dir+'/S_data_HOVMOLLER_'+
#            name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png')
#
##plt.show()
#plt.clf()
#plt.cla()
#plt.close()
#print(X)
#print(Y)
#
## Number of data for Temperature:
## --------------------------------
#cmapTdata=plt.cm.jet
##levels=np.arange(0,250,20)
##csTdata=plt.contourf(Y,X,countT,cmap=cmapTdata,levels=levels,extend='both')
#csTdata=plt.pcolor(Y,X,countT_masked,cmap=cmapTdata,vmin=0, vmax=200)
#print(np.size(rmseT,0))
#print(np.size(rmseT,1))
#plt.xlim([0,np.size(rmseT,0)-2])
#plt.ylim([0,np.size(rmseT,1)-4])
#plt.gca().invert_yaxis()
#plt.xticks(np.arange(0,ncycle,freq_label_plot),years[0::1],
#	rotation=45,fontsize=10,fontweight='bold')
#tdata_name="TEMPERATURE n. DATA "+exp_name
#plt.title(tdata_name,fontsize=12,fontweight='bold')
#plt.xlabel("time",fontsize=10,fontweight='bold')
#plt.ylabel("depth",fontsize=10,fontweight='bold')
#cbar=plt.colorbar(csTdata,orientation="vertical")
#plt.savefig(fig_dir+'/T_data_HOVMOLLER_'+
#	    name_plot+'_'+str(years[0])+'_'+str(years[-1])+'.png')
#
##plt.show()
#plt.clf()
#plt.cla()
#plt.close()
#
#
