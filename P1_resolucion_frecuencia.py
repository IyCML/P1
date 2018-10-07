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



#%% Resolucion
dato = 'int16' 

fs = 44100  


carpeta_salida = 'EstudioFrecuencia'
subcarpeta_salida = 'Resolucion'
subsubcarpeta_salida = str(fs)

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))         

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50
duracion = 1020
muestras = int(fs*duracion)
input_channels = 1
output_channels = 1
amplitud_v_chs_out = [0.5,0.5] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
    
frec_1 = 1003.020
frec_2 = 1003.022
pasos = 1
data_out = np.zeros([pasos,muestras,output_channels])

for i in range(pasos):

    amp = amplitud_chs[0]
    duration = duracion
    
    output_signal = signalgen('sine',frec_1,amp,duration,fs)
    output_signal = output_signal + signalgen('sine',frec_2,amp,duration,fs)
    data_out[i,:,0] = output_signal
        


# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, dato+'_data_out'),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, dato+'_data_in'),data_in)




#%% Figuras
dato = 'int16' 
fs = 44100  
frec_1 = 1003.020
frec_2 = 1003.022
carpeta_salida = 'EstudioFrecuencia'
subcarpeta_salida = 'Resolucion'
subsubcarpeta_salida = str(fs)

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, dato+'_data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, dato+'_data_in.npy'))

### Realiza la FFT de la señal enviada y adquirida
delay = 10
med = 1000
data_in = data_in[:,int(fs*delay):int(fs*(delay+med)),:]
data_out = data_out[:,int(fs*delay):int(fs*(delay+med)),:]

frec_acq,fft_acq_ch0 = fft_power_density(data_in[0,:,0],fs)
frec_acq,fft_out_ch0 = fft_power_density(data_out[0,:,0],fs)


ind_frec = np.argmin(np.abs(frec_acq-frec_1))

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])
ax.plot(frec_acq,10*np.log10(fft_acq_ch0/fft_acq_ch0[ind_frec]),'-',color='blue', label=u'Medición',alpha=0.7)
ax.plot(frec_acq,10*np.log10(fft_out_ch0/fft_out_ch0[ind_frec]),'-',color='red', label=u'Digital',alpha=0.7)
ax.set_xlim([1002.99,1003.06])
ax.set_ylim([-300,50])

ax.grid(linestyle='--')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [dB]')
ax.legend(loc=1)

figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'resolucion_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig) 








