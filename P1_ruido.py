# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 12:36:24 2018

@author: Marco
"""


#%%

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import threading
import datetime
import time
import matplotlib.pylab as pylab
from scipy import signal
from sys import stdout
import numpy.fft as fft
import os
from matplotlib import cm
cmap = cm.get_cmap('jet')

from P1_funciones import play_rec
from P1_funciones import signalgen
from P1_funciones import sincroniza_con_trigger
from P1_funciones import par2ind
from P1_funciones import fft_power_density


params = {'legend.fontsize': 14,
          'figure.figsize': (14, 9),
         'axes.labelsize': 24,
         'axes.titlesize':18,
         'font.size':18,
         'xtick.labelsize':24,
         'ytick.labelsize':24}
pylab.rcParams.update(params)




   
#%%
# CALIBRACION PLACA MARCO PC CASA

carpeta_salida = 'Calibracion'
subcarpeta_salida = 'Parlante'
# Calibracion parlante
amplitud_v_ch0 = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'wp_amp_ch0.npy'))
amplitud_v_ch1 = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'wp_amp_ch1.npy'))
parlante_levels = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'parlante_levels.npy'))
amplitud_v_chs = np.array([amplitud_v_ch0,amplitud_v_ch1])

mic_levels = [10,20,30,40,50,60,70,80,90,100]  
#%%

dato = 'int16' 
carpeta_salida = 'Ruido'
subcarpeta_salida = dato
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))  

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50    
   
fs = 44100*8  
duracion_trigger = 0.5
duracion_ruido = 5
muestras = int(fs*duracion_trigger) + int(fs*duracion_ruido)
input_channels = 2
output_channels = 2
amplitud_v_chs_out = [1.0,1.0] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
fr_trigger = 500
data_out = np.zeros([1,muestras,output_channels])


output_signal_ch0 = signalgen('sine',fr_trigger,amplitud_chs[0],duracion_trigger,fs)
output_signal_ch0 = np.append(output_signal_ch0,np.zeros(int(fs*duracion_ruido)))

output_signal_ch1 = signalgen('sine',fr_trigger,amplitud_chs[1],duracion_trigger,fs)
output_signal_ch1 = np.append(output_signal_ch1,np.zeros(int(fs*duracion_ruido)))
    
data_out[0,:,0] = output_signal_ch0
data_out[0,:,1] = output_signal_ch1
        
# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out'),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in'),data_in)

#%%

dato = 'int16' 
carpeta_salida = 'Ruido'
subcarpeta_salida = dato

par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50    

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1'+   '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))


data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in.npy'))

# Calibracion de los canales
data_in_cal = np.zeros([data_in.shape[0],data_in.shape[1],data_in.shape[2]])
data_in_cal[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in_cal[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])


delay = 3
med = 2
data_in_med = data_in[0,int(fs*delay):int(fs*(delay+med)),:]
data_in_cal_med = data_in_cal[0,int(fs*delay):int(fs*(delay+med)),:]


np.std(data_in_cal_med[:,0])
np.std(data_in_cal_med[:,1])

label0='CH0 - STD: ' + '{:6.3f}'.format(np.std(data_in_cal_med[:,0]*1000)) + ' mV -' + '{:6.1f}'.format(np.std(data_in_med[:,0])) + ' cuentas'
label1='CH1 - STD: ' + '{:6.3f}'.format(np.std(data_in_cal_med[:,1]*1000)) + ' mV -' + '{:6.1f}'.format(np.std(data_in_med[:,1])) + ' cuentas'

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.hist(data_in_cal_med[:,0],bins=10,rwidth=0.9,label=label0,alpha=0.7,align ='mid')
ax.grid(linestyle='--')
ax.set_xlabel(u'Tensión [V]')
ax.set_ylabel(u'Frecuencia [cts.]')
ax.legend()
#ax.set_title(u'Histograma de ruido en tensión del CH0')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruido_v_ch0.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)


fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.hist(data_in_med[:,0],bins=10,rwidth=0.9,label=label0,alpha=0.7,align ='mid')
ax.grid(linestyle='--')
ax.set_xlabel(u'Cuentas')
ax.set_ylabel(u'Frecuencia [cts.]')
ax.legend()
#ax.set_title(u'Histograma de ruido en cuentas del CH0')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruido_cuentas_ch0.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .32, .8])
ax.hist(data_in_cal_med[:,0]*1000,bins=10,rwidth=0.9,label=label1,alpha=0.7,align ='mid')
ax.grid(linestyle='--')
ax.set_xlabel(u'Tensión [mV]')
ax.set_ylabel(u'Frecuencia [cts.]')
ax.legend()
#ax.set_title(u'Histograma de ruido en tensión del CH0')

ax1 = fig.add_axes([.60, .15, .32, .8])
ax1.hist(data_in_med[:,0],bins=10,rwidth=0.9,label=label1,alpha=0.7,align ='mid')
ax1.grid(linestyle='--')
ax1.set_xlabel(u'Cuentas')
ax1.set_ylabel(u'Frecuencia [cts.]')
ax1.legend()
#ax1.set_title(u'Histograma de ruido en cuentas del CH0')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruido_cuentas_v_ch0.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

######


fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.hist(data_in_cal_med[:,1],bins=10,rwidth=0.9,label=label1,alpha=0.7,align ='mid')
ax.grid(linestyle='--')
ax.set_xlabel(u'Tensión [V]')
ax.set_ylabel(u'Frecuencia [cts.]')
ax.legend()
#ax.set_title(u'Histograma de ruido en tensión del CH1')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruido_v_ch1.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)


fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.hist(data_in_med[:,1],bins=10,rwidth=0.9,label=label1,alpha=0.7,align ='mid')
ax.grid(linestyle='--')
ax.set_xlabel(u'Cuentas')
ax.set_ylabel(u'Frecuencia [cts.]')
ax.legend()
#ax.set_title(u'Histograma de ruido en cuentas del CH1')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruido_cuentas_ch1.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .32, .8])
ax.hist(data_in_cal_med[:,1]*1000,bins=10,rwidth=0.9,label=label1,alpha=0.7,align ='mid')
ax.grid(linestyle='--')
ax.set_xlabel(u'Tensión [mV]')
ax.set_ylabel(u'Frecuencia [cts.]')
ax.legend()
#ax.set_title(u'Histograma de ruido en tensión del CH1')

ax1 = fig.add_axes([.60, .15, .32, .8])
ax1.hist(data_in_med[:,1],bins=10,rwidth=0.9,label=label1,alpha=0.7,align ='mid')
ax1.grid(linestyle='--')
ax1.set_xlabel(u'Cuentas')
ax1.set_ylabel(u'Frecuencia [cts.]')
ax1.legend()
#ax1.set_title(u'Histograma de ruido en cuentas del CH1')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruido_cuentas_v_ch1.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



#%% RUIDO EN FUNCION NIVEL MICROFONO


# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
par_level = 30
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 100    

dato = 'int16'    
fs = 44100*8  
duracion_trigger = 0.5
duracion_ruido = 5
muestras = int(fs*duracion_trigger) + int(fs*duracion_ruido)
input_channels = 2
output_channels = 2
amplitud_v_chs_out = [1.0,1.0] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
fr_trigger = 500
data_out = np.zeros([1,muestras,output_channels])


output_signal_ch0 = signalgen('sine',fr_trigger,amplitud_chs[0],duracion_trigger,fs)
output_signal_ch0 = np.append(output_signal_ch0,np.zeros(int(fs*duracion_ruido)))

output_signal_ch1 = signalgen('sine',fr_trigger,amplitud_chs[1],duracion_trigger,fs)
output_signal_ch1 = np.append(output_signal_ch1,np.zeros(int(fs*duracion_ruido)))
    
data_out[0,:,0] = output_signal_ch0
data_out[0,:,1] = output_signal_ch1
        

carpeta_salida = 'Ruido'
subcarpeta_salida = 'NivelMicrofono'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))  

# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out_'+str(mic_level)),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in_'+str(mic_level)),data_in)

#%%

fs = 44100*8  
par_level = 70
ind_nivel = par2ind(par_level,parlante_levels)
dato='int16'

carpeta_salida = 'Ruido'
subcarpeta_salida = 'NivelMicrofono'
delay = 2
med = 3

std_ch0_cts = np.array([])
std_ch1_cts = np.array([])

std_ch0_v = np.array([])
std_ch1_v = np.array([])

ruido_espectro_ch0 = np.array([])
ruido_espectro_ch1 = np.array([])

for i,mic_level in enumerate(mic_levels):

    data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out_'+str(mic_level)+'.npy'))
    data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in_'+str(mic_level)+'.npy'))
    
    calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
    calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
    
    
    # Calibracion de los canales
    data_in_cal = np.zeros([data_in.shape[0],data_in.shape[1],data_in.shape[2]])
    data_in_cal[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
    data_in_cal[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])
      
    data_in_med = data_in[0,int(fs*delay):int(fs*(delay+med)),:]
    data_in_cal_med = data_in_cal[0,int(fs*delay):int(fs*(delay+med)),:]
    
    std_ch0_cts = np.append(std_ch0_cts,np.std(data_in_med[:,0]))
    std_ch1_cts = np.append(std_ch1_cts,np.std(data_in_med[:,1]))
    
    std_ch0_v = np.append(std_ch0_v,np.std(data_in_cal_med[:,0]))    
    std_ch1_v = np.append(std_ch1_v,np.std(data_in_cal_med[:,1]))


    # Espectro
    data_in = data_in_cal
    data_in = data_in[:,int(fs*delay):int(fs*(delay+med)),:]
       
    frec_acq,fft_acq_ch0 = fft_power_density(data_in[0,:,0],fs)
    frec_acq,fft_acq_ch1 = fft_power_density(data_in[0,:,1],fs)    
    

    # Busco frecuencia de testeo
    frec_comparacion = [1020,1025]
    frec_comparacion_ind0 = np.argmin(np.abs(frec_acq-frec_comparacion[0]))
    frec_comparacion_ind1 = np.argmin(np.abs(frec_acq-frec_comparacion[1]))

    ruido_espectro_ch0 = np.append(ruido_espectro_ch0,np.mean(fft_acq_ch0[frec_comparacion_ind0:frec_comparacion_ind1]))
    ruido_espectro_ch1 = np.append(ruido_espectro_ch1,np.mean(fft_acq_ch1[frec_comparacion_ind0:frec_comparacion_ind1]))


mic_levels_array = np.asarray(mic_levels)

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax1=ax.twinx()
ax.plot(mic_levels_array,std_ch0_cts,'o',color='blue',alpha=0.7,label='STD [cuentas]',markersize=10)
ax1.plot(mic_levels_array,std_ch0_v*1000,'o',color='red',alpha=0.7,label='STD [mV]',markersize=10)
ax.set_xlabel(u'Nivel de micrófono')
ax.set_ylabel(u'STD [cuentas]',color='blue')
ax1.set_ylabel(u'STD [mV]',color='red')
ax1.set_ylim([0,1.2])
ax.set_ylim([0.9,1.7])
ax.grid(linestyle='--')
#ax.set_title(u'Desviación estandar del ruido en cuentas y en tensión en función del nivel de micrófono para CH0')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruido_nivel_microfono_ch0.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax1=ax.twinx()
ax.plot(mic_levels_array,std_ch1_cts,'o',color='blue',alpha=0.7,label='STD [cuentas]',markersize=10)
ax1.plot(mic_levels_array,std_ch1_v*1000,'o',color='red',alpha=0.7,label='STD [mV]',markersize=10)
ax.set_xlabel(u'Nivel de micrófono')
ax.set_ylabel(u'STD [cuentas]',color='blue')
ax1.set_ylabel(u'STD [mV]',color='red')
ax1.set_ylim([0,1.2])
ax.set_ylim([0.9,1.7])
ax.grid(linestyle='--')
#ax.set_title(u'Desviación estandar del ruido en cuentas y en tensión en función del nivel de micrófono para CH1')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruido_nivel_microfono_ch1.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

#%% RUIDO POR SNR

par_level = 70
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 100    

dato = 'int16'    
fs = 44100*8  
duracion_trigger = 5
duracion_ruido = 0.5
muestras = int(fs*duracion_trigger) + int(fs*duracion_ruido)
input_channels = 2
output_channels = 2
amplitud_v_chs_out = [0.3,0.3] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
fr_trigger = 1023
data_out = np.zeros([1,muestras,output_channels])


output_signal_ch0 = signalgen('sine',fr_trigger,amplitud_chs[0],duracion_trigger,fs)
output_signal_ch0 = np.append(output_signal_ch0,np.zeros(int(fs*duracion_ruido)))

output_signal_ch1 = signalgen('sine',fr_trigger,amplitud_chs[1],duracion_trigger,fs)
output_signal_ch1 = np.append(output_signal_ch1,np.zeros(int(fs*duracion_ruido)))
    
data_out[0,:,0] = output_signal_ch0
data_out[0,:,1] = output_signal_ch1
        

carpeta_salida = 'Ruido'
subcarpeta_salida = 'SNR'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))  

# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out_'+str(mic_level)),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in_'+str(mic_level)),data_in)



#%%


dato='int16'
par_level = 70
ind_nivel = par2ind(par_level,parlante_levels)
fs = 44100*8  
carpeta_salida = 'Ruido'
subcarpeta_salida = 'SNR'
delay = 1
med = 3

snr_ch0s = np.array([])
snr_ch1s = np.array([])

ruido_espectro_ch0 = np.array([])
ruido_espectro_ch1 = np.array([])

senal_ch0 = np.array([])


for i,mic_level in enumerate(mic_levels):

    data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out_'+str(mic_level)+'.npy'))
    data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in_'+str(mic_level)+'.npy'))    
    
    calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
    calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))  
    
    data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
    data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])    
    
    
    data_in = data_in[:,int(fs*delay):int(fs*(delay+med)),:]
        
    frec_acq,fft_acq_ch0 = fft_power_density(data_in[0,:,0],fs)
    frec_acq,fft_acq_ch1 = fft_power_density(data_in[0,:,1],fs)       

    # Busco frecuencia de testeo
    frec_comparacion = [1020,1025]
    frec_comparacion_ind0 = np.argmin(np.abs(frec_acq-frec_comparacion[0]))
    frec_comparacion_ind1 = np.argmin(np.abs(frec_acq-frec_comparacion[1]))
    frec_testeo_ind0 = frec_comparacion_ind0 + np.argmax(fft_acq_ch0[frec_comparacion_ind0:frec_comparacion_ind1])
    frec_testeo_ind1 = frec_comparacion_ind0 + np.argmax(fft_acq_ch0[frec_comparacion_ind0:frec_comparacion_ind1])
        
    # Ruido de fondo
    frec_comparacion = [1050,1500]
    frec_comparacion_ind0 = np.argmin(np.abs(frec_acq-frec_comparacion[0]))
    frec_comparacion_ind1 = np.argmin(np.abs(frec_acq-frec_comparacion[1]))
    
    # SNR
    snr_ch0 = fft_acq_ch0[frec_testeo_ind0]/np.mean(fft_acq_ch0[frec_comparacion_ind0:frec_comparacion_ind1])
    snr_ch1 = fft_acq_ch1[frec_testeo_ind1]/np.mean(fft_acq_ch1[frec_comparacion_ind0:frec_comparacion_ind1])
    
    snr_ch0s = np.append(snr_ch0s,snr_ch0)
    snr_ch1s = np.append(snr_ch1s,snr_ch1)
    
    ruido_espectro_ch0 = np.append(ruido_espectro_ch0,np.mean(fft_acq_ch0[frec_comparacion_ind0:frec_comparacion_ind1]))
    ruido_espectro_ch1 = np.append(ruido_espectro_ch1,np.mean(fft_acq_ch1[frec_comparacion_ind0:frec_comparacion_ind1]))

mic_levels_array = np.asarray(mic_levels)


fig = plt.figure(dpi=250)
ax = fig.add_axes([.12, .15, .75, .8]) 
ax1 = ax.twinx()    
ax.semilogy(mic_levels_array,snr_ch0s,'o',color='blue',alpha=0.7,label='SNR',markersize=12)
ax1.semilogy(mic_levels_array,ruido_espectro_ch0,'o',color='red',alpha=0.7,label='Ruido',markersize=12)
ax.set_ylim([1e9,1e13])
ax1.set_ylim([1e-13,1e-10])
ax.set_xlabel(u'Nivel de micrófono')
ax.set_ylabel(u'SNR',color='blue')
ax1.set_ylabel(u'Potencia Ruido [$\mathregular{V^2}$sec]',color='red')
ax.grid(linestyle='--')
ax.legend(loc=1)
ax1.legend(loc=4)
#ax.set_title(u'SNR en potencia para señal seno de amplitud 0.3 V para distintos niveles de micrófono para CH0')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'snr_microfono_ch0.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.semilogy(frec_acq,fft_acq_ch1)
ax.legend(bbox_to_anchor=(1.05, 1.00))
ax.set_xlim([1000,1200])
ax.grid(linestyle='--')
#ax.set_title(u'Densidad de potencia espectral para señal seno de amplitud 0.3')
ax.set_xlabel('Frecuencia [Hz]')    
ax.set_ylabel('Potencia [$\mathregular{V^2}$sec]')   
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'potencia_mic100.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

#%% RUIDO EN FRECUENCIA

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
par_level = 70
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 70    

dato = 'int16'    
fs_base = 44100  
duracion_trigger = 0.5
duracion_ruido = 5
input_channels = 2
output_channels = 2
amplitud_v_chs_out = [1.0,1.0] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
fr_trigger = 500

factor = [0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.5,2,2.5,3,3.5,4,5,6,7,8]

carpeta_salida = 'Ruido'
subcarpeta_salida = 'Frecuencia'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))  

for i in range(len(factor)):

    fs = int(fs_base*factor[i])
    muestras = int(fs*duracion_trigger) + int(fs*duracion_ruido)
    data_out = np.zeros([1,muestras,output_channels])

    
    output_signal_ch0 = signalgen('sine',fr_trigger,amplitud_chs[0],duracion_trigger,fs)
    output_signal_ch0 = np.append(output_signal_ch0,np.zeros(int(fs*duracion_ruido)))
    
    output_signal_ch1 = signalgen('sine',fr_trigger,amplitud_chs[1],duracion_trigger,fs)
    output_signal_ch1 = np.append(output_signal_ch1,np.zeros(int(fs*duracion_ruido)))
        
    data_out[0,:,0] = output_signal_ch0
    data_out[0,:,1] = output_signal_ch1        

    # Realiza medicion
    offset_correlacion = 0#int(fs*(1))
    steps_correlacion = 0#int(fs*(1))
    data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)
    
    np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out_'+str(i)),data_out)
    np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in_'+str(i)),data_in)
    
    
#%%

par_level = 70
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 70  

carpeta_salida = 'Ruido'
subcarpeta_salida = 'Frecuencia'

calibracion_CH0_seno = np.load(os.path.join('Calibracion','int16', 'Seno_CH0'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion','int16', 'Seno_CH1'+   '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))



dato = 'int16'    
fs_base = 44100  
duracion_trigger = 0.5
duracion_ruido = 5
input_channels = 2
output_channels = 2
amplitud_v_chs_out = [1.0,1.0] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
fr_trigger = 500

factor = [0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.5,2,2.5,3,3.5,4,5,6,7,8]

carpeta_salida = 'Ruido'
subcarpeta_salida = 'Frecuencia'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))  

delay = 3
med = 1

std_ch0 = np.array([])
std_ch1 = np.array([])

fig = plt.figure(dpi=250)
ax = fig.add_axes([.12, .15, .65, .8])

for i in range(0,len(factor),2):

    fs = int(fs_base*factor[i])
    
    data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out_'+str(i)+'.npy'))
    data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in_'+str(i)+'.npy'))    
    
    # Calibracion de los canales
    data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
    data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])    
    
    
    data_in = data_in[:,int(fs*delay):int(fs*(delay+med)),:]  
    std_ch0 = np.append(std_ch0,np.std(data_in[0,:,0]))
    std_ch1 = np.append(std_ch1,np.std(data_in[0,:,1]))
    
    frec_acq,fft_acq_ch0 = fft_power_density(data_in[0,:,0],fs)
    frec_acq,fft_acq_ch1 = fft_power_density(data_in[0,:,1],fs)       

    ax.loglog(frec_acq,fft_acq_ch1,color=cmap(float(i)/len(factor)),alpha=1/(i+1),label='Frec: ' + '{:6.2f}'.format(fs/1000) + ' kHz')

ax.legend(bbox_to_anchor=(1.05, 1.00))
ax.set_xlim([1,500000])
ax.grid(linestyle='--')
ax.set_xlabel('Frecuencia [Hz]')    
ax.set_ylabel('Potencia [$\mathregular{V^2}$sec]')    
#ax.set_title(u'Potencia espectral para distintas frecuencias de sampleo')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'fft_ruido.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



#%%

carpeta_salida = 'Ruido'
subcarpeta_salida = 'Frecuencia'
dato = 'int16'   
par_level = 70
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 70     
fs_base = 44100  
duracion_trigger = 0.5
duracion_ruido = 5
input_channels = 2
output_channels = 2
amplitud_v_chs_out = [1.0,1.0] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
fr_trigger = 500

factor = [0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.5,2,2.5,3,3.5,4,5,6,7,8]


delay = 2
med = 1

std_ch0 = np.array([])
std_ch1 = np.array([])

for i in range(len(factor)):

    fs = int(fs_base*factor[i])
    
    data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out_'+str(i)+'.npy'))
    data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in_'+str(i)+'.npy'))    
    
    data_in = data_in[:,int(fs*delay):int(fs*(delay+med)),:]  
    std_ch0 = np.append(std_ch0,np.std(data_in[0,:,0]))
    std_ch1 = np.append(std_ch1,np.std(data_in[0,:,1]))
    

vec_promedios = np.arange(1,40)
std_ch0_conv = np.array([])
std_ch1_conv = np.array([])

for i in range(vec_promedios.shape[0]):
    
    data_conv_ch0 = np.convolve(data_in[0,:,0],np.ones(vec_promedios[i])/vec_promedios[i],mode='valid')
    data_conv_ch1 = np.convolve(data_in[0,:,1],np.ones(vec_promedios[i])/vec_promedios[i],mode='valid')
    
    std_ch0_conv = np.append(std_ch0_conv,np.std(data_conv_ch0))
    std_ch1_conv = np.append(std_ch1_conv,np.std(data_conv_ch1))
    
    
factor_array = np.asarray(factor)
frecuencia = factor_array*fs_base
frec_esp = fs_base*8/vec_promedios


fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.plot(frecuencia,std_ch1,'o',markersize=10,label='STD cambiando frec sampleo')    
ax.plot(frec_esp,std_ch1_conv,'-',markersize=10,label='STD dato filtrado')    
ax.grid(linestyle='--')
ax.set_xlabel('Frecuencia sampleo [Hz]')    
ax.set_ylabel('STD [cuentas]')     
#ax.set_title(u'Ruido en función de la frecuencia de sampleo')
ax.legend()
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'std_frec_sampleo.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)    




