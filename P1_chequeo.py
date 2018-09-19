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

params = {'legend.fontsize': 24,
         'figure.figsize': (14, 9),
         'axes.labelsize': 24,
         'axes.titlesize':24,
         'xtick.labelsize':24,
         'ytick.labelsize':24}
pylab.rcParams.update(params)


#%%
    

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
fs = int(44100*8)
duracion = 0.5
muestras = int(fs*duracion)
input_channels = 2
output_channels = 2
amplitud = 1
frec_ini = 1023
frec_fin = 1023
pasos = 1
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
        data_out[i,:,0] = output_signal*np.arange(output_signal.shape[0])/output_signal.shape[0]
        
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

plt.plot(data_in[0,:,1])


#%%

### Corrige retardo y grafica
#
#data_in, retardos = sincroniza_con_trigger(data_out, data_in) 

#%%
ch = 0
step = 0

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .15, .75, .8])
ax1 = ax.twinx()
ax.plot(np.transpose(data_in[step,:,ch]),'-',color='r', label='señal adquirida',alpha=0.5)
ax1.plot(np.transpose(data_out[step,:,ch]),'-',color='b', label='señal enviada',alpha=0.5)
ax.legend(loc=1)
ax1.legend(loc=4)
plt.show()


fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .15, .75, .8])
ax.hist(retardos/fs*1000, bins=100)
ax.set_title(u'Retardos')
ax.set_xlabel('Retardos [ms]')
ax.set_ylabel('Frecuencia')


#%%
### ANALISIS de la señal adquirida. Cheque que la señal adquirida corresponde a la enviada


ch_acq = 0
ch_send = 0
paso = 0

### Realiza la FFT de la señal enviada y adquirida
fft_send = abs(fft.fft(data_out[paso,:,ch_send]))**2/int(data_out.shape[1]/2+1)/fs
fft_send = fft_send[0:int(data_out.shape[1]/2+1)]
fft_send[1:] = 2*fft_send[1:]
fft_acq = abs(fft.fft(data_in[paso,:,ch_acq]))**2/int(data_in.shape[1]/2+1)/fs
fft_acq = fft_acq[0:int(data_in.shape[1]/2+1)]
fft_acq[1:] = 2*fft_acq[1:]

frec_send = np.linspace(0,int(data_out.shape[1]/2),int(data_out.shape[1]/2+1))
frec_send = frec_send*(fs/2+1)/int(data_out.shape[1]/2+1)
frec_acq = np.linspace(0,int(data_in.shape[1]/2),int(data_in.shape[1]/2+1))
frec_acq = frec_acq*(fs/2+1)/int(data_in.shape[1]/2+1)

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax1 = ax.twinx()
ax.plot(frec_send,fft_send,'-' ,label='Frec enviada',alpha=0.7)
ax1.plot(frec_acq,fft_acq,'-',color='red', label=u'Señal adquirida',alpha=0.7)
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Amplitud [a.u.]')
ax.legend(loc=1)
ax1.legend(loc=4)
plt.show()


fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax.plot(frec_acq,fft_acq/fft_send,'-',color='red', label=u'Señal adquirida',alpha=0.7)
ax.set_xlim([0,23000])
ax.set_ylim([0,1e10])
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Amplitud [a.u.]')
ax.legend(loc=1)
plt.show()
 

#%%

Is = 1.0*1e-12
Vt = 26.0*1e-3
n = 1.

Vd = np.linspace(-1,1,1000)
Id = Is*(np.exp(Vd/n/Vt)-1)

Rs = 100
Vs = 1
Ir = Vs/Rs - Vd/Rs


plt.plot(Vd,Id)
plt.plot(Vd,Ir)

