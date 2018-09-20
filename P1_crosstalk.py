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

windows_nivel = np.array([10,20,30,40,50,60,70,80,90,100])
tension_rms_v_ch0 = np.array([0.050, 0.142, 0.284, 0.441, 0.678, 0.884, 1.143, 1.484, 1.771, 2.280])
amplitud_v_ch0 = tension_rms_v_ch0*np.sqrt(2)
tension_rms_v_ch1 = np.array([0.050, 0.146, 0.291, 0.451, 0.693, 0.904, 1.170, 1.518, 1.812, 2.330])
amplitud_v_ch1 = tension_rms_v_ch1*np.sqrt(2)

amplitud_v_chs = np.array([amplitud_v_ch0,amplitud_v_ch1])

#plt.plot(windows_nivel,amplitud_v_ch0,'o')
#plt.plot(windows_nivel,amplitud_v_ch1,'o')

#%%
dato = 'int16' 

carpeta_salida = 'Crosstalk'
subcarpeta_salida = dato
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
ind_nivel = 6
mic_level = 70
fs = 44100*8  
duracion = 13
muestras = int(fs*duracion)
input_channels = 2
output_channels = 1
amplitud_v_chs_out = [1.0,1.0] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
    
frec_ini = 1023
frec_fin = 1023
pasos = 1
delta_frec = (frec_fin-frec_ini)/(pasos+1)
data_out = np.zeros([pasos,muestras,output_channels])

for i in range(pasos):
    parametros_signal = {}
    fs = fs
    amp = amplitud_chs[0]
    fr = frec_ini + i*delta_frec
    duration = duracion
    
    output_signal = signalgen('sine',fr,amp,duration,fs)
    data_out[i,:,0] = output_signal
        


# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida, dato+'_data_out'),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida, dato+'_data_in'),data_in)



#%%

# CAlibracion para nivel de parlante 70, y nivel de microfono de 80
# En este valor de nivel de parlante Amplitud = 1 ==> 1V de amplitud
# En este nivel de parlante la señal de amplitud 1 (1V) ocupa todo el rango de medición
# Esto vale para la placa de pc de escritorio de casa de Marco y windows 10

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, dato+'_data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, dato+'_data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1'+   '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])


### Realiza la FFT de la señal enviada y adquirida
delay = 2
med = 5
data_in = data_in[:,int(fs*delay):int(fs*(delay+med)),:]


fft_acq_ch0 = abs(fft.fft(data_in[0,:,0]))**2/int(data_in.shape[1]/2+1)/fs
fft_acq_ch0 = fft_acq_ch0[0:int(data_in.shape[1]/2+1)]
fft_acq_ch0[1:] = 2*fft_acq_ch0[1:]

fft_acq_ch1 = abs(fft.fft(data_in[0,:,1]))**2/int(data_in.shape[1]/2+1)/fs
fft_acq_ch1 = fft_acq_ch1[0:int(data_in.shape[1]/2+1)]
fft_acq_ch1[1:] = 2*fft_acq_ch1[1:]

frec_acq = np.linspace(0,int(data_in.shape[1]/2),int(data_in.shape[1]/2+1))
frec_acq = frec_acq*(fs/2+1)/int(data_in.shape[1]/2+1)
        
# Busco frecuencia de testeo
frec_comparacion = [1020,1025]
frec_comparacion_ind0 = np.argmin(np.abs(frec_acq-frec_comparacion[0]))
frec_comparacion_ind1 = np.argmin(np.abs(frec_acq-frec_comparacion[1]))
frec_testeo_ind0 = frec_comparacion_ind0 + np.argmax(fft_acq_ch0[frec_comparacion_ind0:frec_comparacion_ind1])
frec_testeo_ind1 = frec_comparacion_ind0 + np.argmax(fft_acq_ch0[frec_comparacion_ind0:frec_comparacion_ind1])

# Ruido de fondo
frec_comparacion = [1050,1100]
frec_comparacion_ind0 = np.argmin(np.abs(frec_acq-frec_comparacion[0]))
frec_comparacion_ind1 = np.argmin(np.abs(frec_acq-frec_comparacion[1]))

# SNR
snr_ch0 = fft_acq_ch0[frec_testeo_ind0]/np.mean(fft_acq_ch0[frec_comparacion_ind0:frec_comparacion_ind1])
snr_ch1 = fft_acq_ch1[frec_testeo_ind1]/np.mean(fft_acq_ch1[frec_comparacion_ind0:frec_comparacion_ind1])

snr_ch0/snr_ch1

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])
ax.semilogy(frec_acq,fft_acq_ch0,'-',color='blue', label=u'Canal con señal - SNR: ' + '{:6.1e}'.format(snr_ch0),alpha=0.7)
ax.semilogy(frec_acq,fft_acq_ch1,'-',color='red', label=u'Canal sin señal - SNR: ' + '{:6.1e}'.format(snr_ch1),alpha=0.7)
ax.set_xlim([1010,1040])
ax.set_ylim([1e-15,1e1])
ax.grid(linestyle='--')
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [$\mathregular{V^2}$sec]')
ax.set_title(u'Medición de crosstalk. Potencia de señal en dos canales. Señal enviada a 1023 Hz')
ax.legend(loc=1)
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'crosstalk.png')
fig.savefig(figname, dpi=300)  
plt.close(fig) 
       

