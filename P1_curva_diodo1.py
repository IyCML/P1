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
from P1_funciones import signalgen_corrected
from P1_funciones import sincroniza_con_trigger

params = {'legend.fontsize': 'large',
     #     'figure.figsize': (15, 5),
         'axes.labelsize': 'large',
         'axes.titlesize':'medium',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)


#%%

windows_nivel = np.array([10,20,30,40,50,60,70,80,90,100])
tension_rms_v_ch0 = np.array([0.050, 0.142, 0.284, 0.441, 0.678, 0.884, 1.143, 1.484, 1.771, 2.280])
amplitud_v_ch0 = tension_rms_v_ch0*np.sqrt(2)
tension_rms_v_ch1 = np.array([0.050, 0.146, 0.291, 0.451, 0.693, 0.904, 1.170, 1.518, 1.812, 2.330])
amplitud_v_ch1 = tension_rms_v_ch1*np.sqrt(2)

amplitud_v_chs = np.array([amplitud_v_ch0,amplitud_v_ch1])

#%%


carpeta_salida = 'CurvaDiodo'
subcarpeta_salida = 'Curvas1'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     
    

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
dato = 'int16'    
ind_nivel = 6
mic_level = 70
fs = 44100*8  
duracion = 5
muestras = int(fs*duracion) + int(fs*1)
input_channels = 2
output_channels = 2
amplitud_v_chs_out = [1.60,1.60] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
    
frec_ini = 10
frec_fin = 10
pasos_frec = 1
delta_frec = (frec_fin-frec_ini)/(pasos_frec+1)
data_out = np.zeros([pasos_frec,muestras,output_channels])

# Para corregir segun la respuesta
fft_norm = np.load(os.path.join('Respuesta','Chirp', 'respuesta_potencia_chirp.npy'))
frec_send = np.load(os.path.join('Respuesta','Chirp', 'frecuencia_chirp.npy'))


for i in range(pasos_frec):
    parametros_signal = {}
    fs = fs
    fr = frec_ini + i*delta_frec
    duration = duracion
    
    for j in range(output_channels):
        amp = amplitud_chs[j]
        
        if j == 0:
            output_signal = signalgen('square',fr,amp,duration,fs)
            output_signal = np.append(output_signal,np.zeros(int(fs*1)))
            data_out[i,:,j] = output_signal
            
        if j == 1:
            output_signal = signalgen_corrected('square',fr,amp,duration,fs,frec_send,fft_norm,[2,20500])
            output_signal = np.append(output_signal,np.zeros(int(fs*1)))
            data_out[i,:,j] = output_signal        
        
plt.plot(output_signal)

# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out'),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in'),data_in)

#%%


fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .15, .75, .8])
ax1 = ax.twinx()
ax.plot(data_in[0,:,0] ,alpha=0.8)
ax1.plot(data_in[0,:,1] ,color='red',alpha=0.8)
ax1.set_ylim([-3000,3000])

#%%


fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .15, .75, .8])
ax1 = ax.twinx()
ax.semilogy(np.abs(fft.fft(data_out[0,:,0])),alpha=0.8)
ax1.semilogy(np.abs(fft.fft(data_out[0,:,1])) ,color='red',alpha=0.8)



#%%

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .15, .75, .8])
ax1 = ax.twinx()
ax.plot(caida_tot ,alpha=0.8)
ax1.plot(caida_res ,color='red',alpha=0.8)
#ax1.plot(caida_diodo ,color='red',alpha=0.8)

#
#
#ax1.plot(data_out[0,:,0],alpha=0.8)



#%% AJuste de curvas

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0_wp'+ str(windows_nivel[ind_nivel]) +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1_wp'+ str(windows_nivel[ind_nivel]) +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])

offset = 0.198 #R150

resistencia = 149
delay = 3
med = 0.5
caida_tot = -data_in[0,int(fs*delay):int(fs*(delay+med)),0]
caida_res = -data_in[0,int(fs*delay)-4:int(fs*(delay+med))-4,1]+offset#+ np.max(data_in[0,int(fs*delay):int(fs*(delay+med)),1])
caida_diodo = caida_tot - caida_res
i_res = caida_res/resistencia


fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .15, .75, .8])
ax1 = ax.twinx()
ax.plot(caida_tot ,alpha=0.8)
ax.plot(caida_res ,color='red',alpha=0.8)
ax1.plot(caida_res/caida_tot ,color='green',alpha=0.8)






#%%

paso = 0
ch_send = 0
ch_acq = 0
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
ax.semilogy(frec_send,fft_send,'-' ,label='Frec enviada',alpha=0.7)
ax1.semilogy(frec_acq,fft_acq,'-',color='red', label=u'Señal adquirida',alpha=0.7)
ax.legend()


frec_ind1 = np.argmin(np.abs(frec_send-20500))
fft_send_cortada1 = fft.fft(data_out[paso,:,ch_send])
fft_send_cortada1[frec_ind1:] = 0
senal_cortada1 = fft.ifft(fft_send_cortada1)

frec_ind2 = np.argmin(np.abs(frec_send-7050))
fft_send_cortada2 = fft.fft(data_out[paso,:,ch_send])
fft_send_cortada2[frec_ind2:] = 0
senal_cortada2 = fft.ifft(fft_send_cortada2)

plt.plot(np.real(senal_cortada1))
plt.plot(np.real(senal_cortada2))


#%%






#%%

Is = 1.0*1e-12
Vt = 26.0*1e-3
n = 1.0

vpico = 1

Vd = np.linspace(-vpico,vpico,1000)
Id = Is*(np.exp(Vd/n/Vt)-1)

Rs = 50

plt.plot(Vd,Id)

#Rs = 50
#for i in range(-10,10):
#    Vs = 0.1*i
#    Ir = Vs/Rs - Vd/Rs
#    plt.plot(Vd,Ir,color='blue')
   
Rs = 500    
for i in range(-10,10):
    Vs = 0.1*i
    Ir = Vs/Rs - Vd/Rs
    plt.plot(Vd,Ir,color='red')    
    
 

plt.ylim([-0.2e-2,0.05])




