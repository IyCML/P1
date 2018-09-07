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
duracion = 0.1
muestras = int(fs*duracion)
input_channels = 2
output_channels = 1
amplitud = 1
frec_ini = 500
frec_fin = 500
pasos_frec = 1
delta_frec = (frec_fin-frec_ini)/(pasos_frec+1)
data_out = np.zeros([pasos_frec,muestras,output_channels])

for i in range(pasos_frec):
    parametros_signal = {}
    fs = fs
    amp = amplitud
    fr = frec_ini + i*delta_frec
    duration = duracion
    
    
    output_signal = signalgen('ramp',fr,amp,duration,fs)
    data_out[i,:,0] = output_signal
        
        


# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion)

caida_tot = data_in[0,:,0]
caida_res = data_in[0,:,1]
caida_diodo = caida_tot - caida_res
i_res = caida_res/100

plt.plot(-caida_diodo,-i_res)


carpeta_salida = 'curva_diodo'
os.mkdir(carpeta_salida)

np.save(os.path.join(carpeta_salida, 'data_out_ramp'),data_out)
np.save(os.path.join(carpeta_salida, 'data_in_ramp'),data_in)

ch = 1
step = 0

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .15, .75, .8])
ax1 = ax.twinx()
ax.plot(np.transpose(data_in[step,:,1]),'-',color='r', label='señal adquirida',alpha=0.5)
ax1.plot(np.transpose(data_in[step,:,0]),'-',color='b', label='señal enviada',alpha=0.5)
ax.legend(loc=1)
ax1.legend(loc=4)
plt.show()


#%%

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
fs = 44100*8  
duracion = 0.1
muestras = int(fs*duracion)
input_channels = 2
output_channels = 1
amplitud = 1
frec_ini = 500
frec_fin = 500
pasos_frec = 1
delta_frec = (frec_fin-frec_ini)/(pasos_frec+1)
data_out = np.zeros([pasos_frec,muestras,output_channels])

for i in range(pasos_frec):
    parametros_signal = {}
    fs = fs
    amp = amplitud
    fr = frec_ini + i*delta_frec
    duration = duracion
    
    
    output_signal = signalgen('sine',fr,amp,duration,fs)
    data_out[i,:,0] = output_signal
        
        


# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion)

caida_tot = data_in[0,:,0]
caida_res = data_in[0,:,1]
caida_diodo = caida_tot - caida_res

plt.plot(caida_diodo)
