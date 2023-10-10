import numpy as np
import sys
import os.path
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
import csv
from pylab import figure, show, legend, ylabel


#set path 
path1='./for_val_EAS5/RMSDIR/'
fig_dir='./'

infile1=path1+'rms_sla_0.txt'
inf=open(infile1)
csvl = csv.reader(inf, delimiter=" ") 
rows = list(zip(*csvl))
#nlines=np.shape(rows)[105:105,0]
rms_sla = np.asarray(rows[1]).astype(float) * 100
rms_sla_exp1 = rms_sla[105:261]
num_sla = np.asarray(rows[2]).astype(float) 
num_sla_exp1 = num_sla[105:261]
name1='All satellites'
times_list = rows[0]
times_list = times_list[105:261]
times = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in times_list]
nlines = np.shape(rms_sla[105:261])[0]
times = np.asarray(times)
data_1 = times[0]
data_2 = times[1]
if data_2 - data_1 == datetime.timedelta(7):
    times1 = pd.date_range(str(data_1), periods=nlines, freq="7d")
else:
    times1 = pd.date_range(str(data_1), periods=nlines, freq="1d")

infile2=path1+'rms_sla_1.txt'
inf=open(infile2)
csvl = csv.reader(inf, delimiter=" ")
rows = list(zip(*csvl))
rms_sla = np.asarray(rows[1]).astype(float) * 100
rms_sla_exp2 = rms_sla[105:261]
name2='Sentinel3A'

infile3=path1+'rms_sla_2.txt'
inf=open(infile3)
csvl = csv.reader(inf, delimiter=" ")
rows = list(zip(*csvl))
rms_sla = np.asarray(rows[1]).astype(float) * 100
rms_sla_exp3 = rms_sla[105:261]
name3='CryoSat2'
 
infile4=path1+'rms_sla_3.txt'
inf=open(infile4)
csvl = csv.reader(inf, delimiter=" ")
rows = list(zip(*csvl))
rms_sla = np.asarray(rows[1]).astype(float) * 100
rms_sla_exp4 = rms_sla[105:261]
name4='Jason3'

infile5=path1+'rms_sla_5.txt'
inf=open(infile5)
csvl = csv.reader(inf, delimiter=" ")
rows = list(zip(*csvl))
rms_sla = np.asarray(rows[1]).astype(float) * 100
rms_sla_exp5 = rms_sla[105:261]
name5='Jason2'

infile6=path1+'rms_sla_6.txt'
inf=open(infile6)
csvl = csv.reader(inf, delimiter=" ")
rows = list(zip(*csvl))
rms_sla = np.asarray(rows[1]).astype(float) * 100
rms_sla_exp6 = rms_sla[105:261]
name6='Altika'

infile7=path1+'rms_sla_4.txt'
inf=open(infile7)
csvl = csv.reader(inf, delimiter=" ")
rows = list(zip(*csvl))
rms_sla = np.asarray(rows[1]).astype(float) * 100
rms_sla_exp7 = rms_sla[105:261]
name7='Sentinel3B'
    
rms_sla_exp1[rms_sla_exp1 == 0]=np.nan
rms_sla_exp2[rms_sla_exp2 == 0]=np.nan
rms_sla_exp3[rms_sla_exp3 == 0]=np.nan
rms_sla_exp4[rms_sla_exp4 == 0]=np.nan
rms_sla_exp5[rms_sla_exp5 == 0]=np.nan
rms_sla_exp6[rms_sla_exp6 == 0]=np.nan       
rms_sla_exp7[rms_sla_exp7 == 0]=np.nan
 
RMS_1=np.round(np.nanmean(rms_sla_exp1),2)
RMS_2=np.round(np.nanmean(rms_sla_exp2),2)
RMS_3=np.round(np.nanmean(rms_sla_exp3),2)
RMS_4=np.round(np.nanmean(rms_sla_exp4),2)
RMS_5=np.round(np.nanmean(rms_sla_exp5),2)
RMS_6=np.round(np.nanmean(rms_sla_exp6),2)
RMS_7=np.round(np.nanmean(rms_sla_exp7),2)

#fig = plt.figure(figsize=(9,5.5))
fig = plt.figure(figsize=(15,8))
plt.rc('xtick',labelsize=14)
plt.rc('ytick',labelsize=14)
ax = fig.add_subplot(111)

plt.fill_between(times1,num_sla_exp1,color="gray", alpha=0.4)
ax.yaxis.tick_right()
ax.yaxis.set_label_position("right")
ax.set_ylim([0,4000])
ax.yaxis.set_ticks(np.arange(0, 4000+0.1, 1000))
ylabel("Number of measurements",fontsize=16)
ax1 = fig.add_subplot(111, sharex=ax, frameon=False)
#line1 = ax1.plot(times1,rms_sla_exp1,'-k',linewidth=3.0,label=name1)
line1 = ax1.plot(times1,rms_sla_exp6,'-y',label=name6)
#line1 = ax.plot(times1,rms_sla_exp2,'-b',label=name2)
line1 = ax1.plot(times1,rms_sla_exp3,'-r',label=name3)
line1 = ax1.plot(times1,rms_sla_exp5,'-m',label=name5)
line1 = ax1.plot(times1,rms_sla_exp4,'-g',label=name4)
#line1 = ax.plot(times1,rms_sla_exp5,'-m',label=name5)
line1 = ax1.plot(times1,rms_sla_exp2,'-b',label=name2)
line1 = ax1.plot(times1,rms_sla_exp7,'-c',label=name7)
line1 = ax1.plot(times1,rms_sla_exp1,'-k',linewidth=3.0,label=name1)
ylabel("SLA Root mean square misfit [cm]",fontsize=16,color='k')

#ax.xaxis.set_major_locator(mdates.YearLocator())
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
datemin = np.datetime64(times1[0], 'm')
datemax = np.datetime64(times1[-1], 'm') + np.timedelta64(1, 'm')
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax1.set_xlim(datemin, datemax)

#ax1.legend(loc='best', ncol=4, shadow=True,fontsize=14)
#handles, labels = plt.gca().get_legend_handles_labels()
#order = [6,0,1,2,3,4,5]
#plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order])
ax1.legend(loc='lower center', ncol=4, shadow=True,fontsize=14)

ax1.set_ylim([2.,6.])
ax1.yaxis.set_ticks(np.arange(2., 6.0+.01, 0.5))


#ax.set_title('RMS satellite-model misfit, cm \n Satellite',fontsize=18)       #ax.set_title(title, fontsize=18)
ax1.grid('on',linestyle='--')
fig.autofmt_xdate()
       #    plt.gcf().autofmt_xdate()
plt.savefig(fig_dir +'rms_sla_14.png')
plt.close('all') 
#plt.show()

 
