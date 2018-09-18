# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 11:48:50 2018

@author: Marco

"""

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
from scipy.optimize import curve_fit


from P1_funciones import play_rec
from P1_funciones import signalgen
from P1_funciones import signalgen_corrected
from P1_funciones import sincroniza_con_trigger

params = {'legend.fontsize': 'large',
     #     'figure.figsize': (15, 5),
         'axes.labelsize': 'large',
         'axes.titlesize':'medium',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)


windows_nivel = np.array([10,20,30,40,50,60,70,80,90,100])
tension_rms_v_ch0 = np.array([0.050, 0.142, 0.284, 0.441, 0.678, 0.884, 1.143, 1.484, 1.771, 2.280])
amplitud_v_ch0 = tension_rms_v_ch0*np.sqrt(2)
tension_rms_v_ch1 = np.array([0.050, 0.146, 0.291, 0.451, 0.693, 0.904, 1.170, 1.518, 1.812, 2.330])
amplitud_v_ch1 = tension_rms_v_ch1*np.sqrt(2)

amplitud_v_chs = np.array([amplitud_v_ch0,amplitud_v_ch1])


# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
dato = 'int16'    
ind_nivel = 6
mic_level = 70
fs = 44100*8  
duracion = 1
muestras = int(fs*duracion) + int(fs*0)
input_channels = 2
output_channels = 1
amplitud_v_chs_out = [1.50,1.50] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
    
frec_ini = 500
frec_fin = 500
pasos_frec = 1
delta_frec = (frec_fin-frec_ini)/(pasos_frec+1)
data_out = np.zeros([pasos_frec,muestras,output_channels])

## Para corregir segun la respuesta
#fft_norm = np.load(os.path.join('Respuesta','Chirp', 'respuesta_potencia_chirp.npy'))
#frec_send = np.load(os.path.join('Respuesta','Chirp', 'frecuencia_chirp.npy'))

for i in range(pasos_frec):
    parametros_signal = {}
    fs = fs
    fr = frec_ini + i*delta_frec
    duration = duracion
    
    for j in range(output_channels):
        amp = amplitud_chs[j]
        output_signal = signalgen('sine',fr,amp,duration,fs)
        output_signal = np.append(output_signal,np.zeros(int(fs*0)))
#        output_signal = signalgen_corrected('square',fr,amp,duration,fs,frec_send,fft_norm,[2,20500])
#        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
        data_out[i,:,j] = output_signal
        
        

output_signal[output_signal < 0] = 0
fft_0 = fft.fft(output_signal)

corte = 10
fft_1 = fft_0
fft_1[0:corte] = 0
fft_1[len(fft_1)-corte:] = 0

output_signal_1 = np.real(fft.ifft(fft_1))



plt.plot(output_signal)
plt.plot(output_signal_1)

        