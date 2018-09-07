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


from P1_funciones import play_rec
from P1_funciones import signalgen
from P1_funciones import sincroniza_con_trigger

params = {'legend.fontsize': 'large',
     #     'figure.figsize': (15, 5),
         'axes.labelsize': 'large',
         'axes.titlesize':'medium',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)


#%%
    

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
fs = 44100*8  
duracion = 0.5
muestras = int(fs*duracion)
input_channels = 2
output_channels = 2
amplitud = 1
frec_ini = 1000
frec_fin = 1000
pasos = 2
delta_frec = (frec_fin-frec_ini)/(pasos+1)
data_out = np.zeros([pasos,muestras,output_channels])

for i in range(pasos):
    parametros_signal = {}
    fs = fs
    amp = amplitud
    fr = frec_ini + i*delta_frec
    duration = duracion
    
    if i == 0:
        output_signal = signalgen('sine',fr,amp,duration,fs)
        data_out[i,:,0] = output_signal
        
        output_signal = signalgen('sine',fr,amp,duration,fs)
        data_out[i,:,1] = output_signal

    if i == 1:
        output_signal = signalgen('ramp',fr,amp,duration,fs)
        data_out[i,:,0] = output_signal
        
        output_signal = signalgen('ramp',fr,amp,duration,fs)
        data_out[i,:,1] = output_signal

# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion)

plt.plot(np.transpose(data_in[1,:,0]))

#%% Medimos linealidad en amplitud
#Linealidad para seno

carpeta_salida = 'linealidad'
os.mkdir(carpeta_salida)

lin_sen_ch0 = data_in[0,:,0]/data_out[0,:,0]
lin_sen_ch1 = data_in[0,:,1]/data_out[0,:,1]
lin_ramp_ch0 = data_in[1,:,0]/data_out[1,:,0]
lin_ramp_ch1 = data_in[1,:,1]/data_out[1,:,1]

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .15, .75, .8])
ax.plot(data_out[0,int(fs*0.1):-int(fs*0.1),0],data_in[0,int(fs*0.1):-int(fs*0.1),0],'.',label='Seno en CH0',markersize=1)
ax.plot(data_out[0,int(fs*0.1):-int(fs*0.1),1],data_in[0,int(fs*0.1):-int(fs*0.1),1],'.',label='Seno en CH1',markersize=1)
ax.plot(data_out[1,int(fs*0.1):-int(fs*0.1),0],data_in[1,int(fs*0.1):-int(fs*0.1),0],'.',label='Rampa en CH0',markersize=1)
ax.plot(data_out[1,int(fs*0.1):-int(fs*0.1),1],data_in[1,int(fs*0.1):-int(fs*0.1),1],'.',label='Rampa en CH1',markersize=1)
ax.set_xlabel('señal enviada')
ax.set_ylabel('señal recibida [u.a.]')
ax.legend(loc=2)
ax.grid(linestyle='--')
figname = os.path.join(carpeta_salida, 'calibracion.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

np.save(os.path.join(carpeta_salida, 'data_out'),data_out)
np.save(os.path.join(carpeta_salida, 'data_in'),data_in)



