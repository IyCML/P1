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
from scipy.optimize import curve_fit
from matplotlib import cm
cmap = cm.get_cmap('jet')


from P1_funciones import play_rec
from P1_funciones import signalgen
from P1_funciones import signalgen_corrected
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

def func_exp(x, a, b, c):
    return a * np.exp(x/b) + c

def func_ganancia_opamp(x, a, b, c, d):
    return a/(b+c*x) + d

#%%

carpeta_salida = 'LM324'
subcarpeta_salida = 'Seguidor'
subsubcarpeta_salida = '0V'

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))        

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
dato = 'int16'    
par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50
fs = 44100*8  
duracion = 1
muestras = int(fs*duracion) + int(fs*1)
input_channels = 2
output_channels = 1
amplitud_v_chs_out = [2.1,2.1] #V
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
        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
#        output_signal = signalgen_corrected('square',fr,amp,duration,fs,frec_send,fft_norm,[2,20500])
#        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
        data_out[i,:,j] = output_signal
        
        


# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out'),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in'),data_in)

#%% FIGURA

carpeta_salida = 'LM324'
subcarpeta_salida = 'Seguidor'
subsubcarpeta_salida = '0V'

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])
tiempo = np.linspace(0,data_in.shape[1]-1,data_in.shape[1])/fs

med = 0.1
delay = 0.5

input_signal = data_in[0,int(fs*delay):int(fs*delay)+int(fs*med),0]
output_signal = data_in[0,int(fs*delay):int(fs*delay)+int(fs*med),1]
tiempo_signal = tiempo[int(fs*delay):int(fs*delay)+int(fs*med)]

input_signal = input_signal + 0.3125
output_signal = output_signal + 0.1027
output_signal_corrected = output_signal + 0.6137

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .32, .8])

ax.plot(tiempo_signal,input_signal,'-',label='Input',alpha=0.8)
ax.plot(tiempo_signal,output_signal,'-',color='red',label='Output',alpha=0.8)
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [s]')
ax.set_ylabel(u'Tensión [V]')
#ax.set_title('Offset por ancho de banda corregido')
ax.set_xlim([0.5,0.505])

ax1 = fig.add_axes([.60, .15, .32, .8])
ax1.plot(tiempo_signal,input_signal,'-',label='Input',alpha=0.8)
ax1.plot(tiempo_signal,output_signal_corrected,'-',color='red',label='Output + offset',alpha=0.8)
ax1.axhline(0.6137,linestyle='--',color='black',alpha=0.7,label=u'Tensión recorte')
ax1.legend()
ax1.grid(linestyle='--')
ax1.set_xlabel(u'Tiempo [s]')
#ax1.set_ylabel(u'Tensión [V]')
ax1.set_xlim([0.5,0.505])
#ax1.set_title('Offset por recorte corregido')
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'salida_diodo_recortada.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)


#%%

carpeta_salida = 'LM324'
subcarpeta_salida = 'Seguidor'
subsubcarpeta_salida = '-5V'

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))        

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
dato = 'int16'    
par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50
fs = 44100*8  
duracion = 1
muestras = int(fs*duracion) + int(fs*1)
input_channels = 2
output_channels = 1
amplitud_v_chs_out = [1.5,1.5] #V
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
        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
#        output_signal = signalgen_corrected('square',fr,amp,duration,fs,frec_send,fft_norm,[2,20500])
#        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
        data_out[i,:,j] = output_signal
        
        


# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out'),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in'),data_in)



#%% FIGURA

carpeta_salida = 'LM324'
subcarpeta_salida = 'Seguidor'
subsubcarpeta_salida = '-5V'

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])
tiempo = np.linspace(0,data_in.shape[1]-1,data_in.shape[1])/fs

med = 0.1
delay = 0.5

input_signal = data_in[0,int(fs*delay):int(fs*delay)+int(fs*med),0]
output_signal = data_in[0,int(fs*delay):int(fs*delay)+int(fs*med),1]
tiempo_signal = tiempo[int(fs*delay):int(fs*delay)+int(fs*med)]

input_signal = input_signal + 0.1622
output_signal = output_signal+ 0.1622

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .32, .8])

ax.plot(tiempo_signal,input_signal,'-',label='Input',alpha=0.8)
ax.plot(tiempo_signal,output_signal,'-',color='red',label='Output',alpha=0.8)
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [s]')
ax.set_ylabel(u'Tensión [V]')
#ax.set_title('Offset por ancho de banda corregido')
ax.set_xlim([0.5,0.505])

ax1 = fig.add_axes([.60, .15, .32, .8])
ax1.plot(tiempo_signal,input_signal,'-',label='Input',alpha=0.8)
ax1.plot(tiempo_signal,output_signal,'-',color='red',label='Output',alpha=0.8)
ax1.legend()
ax1.grid(linestyle='--')
ax1.set_xlabel(u'Tiempo [s]')
#ax1.set_ylabel(u'Tensión [V]')
ax1.set_xlim([0.5027,0.5037])
ax1.set_ylim([-0.01,0.00])
#ax1.set_title('Detalle ripple caida')

figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'salida_diodo.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



#%%

carpeta_salida = 'LM324'
subcarpeta_salida = 'Seguidor'
subsubcarpeta_salida = 'SlewRate_-5V'

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))        

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
dato = 'int16'    
par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50
fs = 44100*8  
duracion = 1
muestras = int(fs*duracion) + int(fs*1)
input_channels = 2
output_channels = 1

amplitud_v_chs_out = [1.5,1.5] #V
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
        output_signal = signalgen('ramp',fr,amp,duration,fs)
        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
#        output_signal = signalgen_corrected('square',fr,amp,duration,fs,frec_send,fft_norm,[2,20500])
#        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
        data_out[i,:,j] = output_signal
        
        


# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out'),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in'),data_in)



#%% FIGURAS

carpeta_salida = 'LM324'
subcarpeta_salida = 'Seguidor'
subsubcarpeta_salida = 'SlewRate_-5V'

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])
tiempo = np.linspace(0,data_in.shape[1]-1,data_in.shape[1])/fs

med = 0.1
delay = 0.5

input_signal = data_in[0,int(fs*delay):int(fs*delay)+int(fs*med),0]
output_signal = data_in[0,int(fs*delay):int(fs*delay)+int(fs*med),1]
tiempo_signal = tiempo[int(fs*delay):int(fs*delay)+int(fs*med)]

input_signal = input_signal + 0.1622
output_signal = output_signal+ 0.1622

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .32, .8])

ax.plot(tiempo_signal,input_signal,'-',label='Input',alpha=0.8)
ax.plot(tiempo_signal,output_signal,'-',color='red',label='Output',alpha=0.8)
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [s]')
ax.set_ylabel(u'Tensión [V]')
#ax.set_title('Offset por ancho de banda corregido')
ax.set_xlim([0.5,0.505])

ax1 = fig.add_axes([.60, .15, .32, .8])
ax1.plot(tiempo_signal,input_signal,'-',label='Input',alpha=0.8)
ax1.plot(tiempo_signal,output_signal,'-',color='red',label='Output',alpha=0.8)
ax1.legend()
ax1.grid(linestyle='--')
ax1.set_xlabel(u'Tiempo [s]')
#ax1.set_ylabel(u'Tensión [V]')
ax1.set_xlim([0.5027,0.5037])
ax1.set_ylim([-0.01,0.00])
#ax1.set_title('Detalle ripple caida')

figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'salida_diodo.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



#%% RESPUESTA

carpeta_salida = 'LM324'
subcarpeta_salida = 'Seguidor'
subsubcarpeta_salida = 'Respuesta_-5V'

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))


fs = 44100*8  
duracion = 30
muestras = int(fs*duracion)
input_channels = 2
output_channels = 1
par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50

amplitud_v_chs_out = [1.5,1.5] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
    
amplitud = amplitud_chs[0]   

# Frecuencias bajas
frec_ini = 0
frec_fin = 23000
output_signal = amplitud*signal.chirp(np.arange(muestras)/fs,frec_fin,duracion,frec_ini)
ceros = np.zeros(int(fs*1))
output_signal = np.append(output_signal,ceros,axis=0)
output_signal = np.append(ceros,output_signal,axis=0)
data_out1 = np.zeros([1,output_signal.shape[0],output_channels])
data_out1[0,:,0] = output_signal


offset_correlacion = int(fs*(5))
steps_correlacion = int(fs*(0.1))
data_in1, retardos1 = play_rec(fs,input_channels,data_out1,'si',offset_correlacion,steps_correlacion)


###
frec_comp = 10000

frec_send,fft_send = fft_power_density(data_out1[0,:,0],fs)
frec_acq,fft_acq_input = fft_power_density(data_in1[0,:,0],fs)
frec_acq,fft_acq_output = fft_power_density(data_in1[0,:,1],fs)   

frec_ind_acq = np.argmin(np.abs(frec_acq-frec_comp))
frec_ind_send = np.argmin(np.abs(frec_send-frec_comp))



fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .32, .8])
ax.semilogy(frec_send,fft_acq_output/fft_acq_output[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)
ax.semilogy(frec_send,fft_acq_input/fft_acq_input[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
ax.semilogy(frec_send,fft_send/fft_send[frec_ind_send],'-', label=u'Send',alpha=0.6,linewidth=2)

ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
#ax.set_title(u'FFT de la señal digital, input y output para seguidor LM324')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')

ax1 = fig.add_axes([.60, .15, .32, .8])
ax1.semilogy(frec_send,fft_acq_output/fft_acq_output[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)
ax1.semilogy(frec_send,fft_acq_input/fft_acq_input[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
ax1.semilogy(frec_send,fft_send/fft_send[frec_ind_send],'-', label=u'Send',alpha=0.6,linewidth=2)

ax1.set_xlim([-10,200])
ax1.set_ylim([1e-3,1e1])
#ax1.set_title(u'Detalle a baja frecuencia')
ax1.set_xlabel('Frecuencia [Hz]')
ax1.set_ylabel('Potencia [db]')
ax1.legend(loc=1)
ax1.grid(linewidth=0.5,linestyle='--')

figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'chirp.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



fft_norm_input = fft_acq_input/fft_acq_input[frec_ind_send]/(fft_send/fft_send[frec_ind_send])
fft_norm_output = fft_acq_output/fft_acq_output[frec_ind_send]/(fft_send/fft_send[frec_ind_send])
fft_norm_norm_output = fft_norm_output/fft_norm_output[frec_ind_send]/(fft_norm_input/fft_norm_input[frec_ind_send])


## Normalizada
fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .32, .8])
ax.semilogy(frec_send,fft_norm_input/fft_norm_input[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
ax.semilogy(frec_send,fft_norm_output/fft_norm_output[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)

ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
#ax.set_title(u'FFT normalizada de la señal input y output para seguidor LM324')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')

ax1 = fig.add_axes([.60, .15, .32, .8])
ax1.semilogy(frec_send,fft_norm_input/fft_norm_input[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
ax1.semilogy(frec_send,fft_norm_output/fft_norm_output[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)

ax1.set_xlim([-10,200])
ax1.set_ylim([1e-3,1e1])
#ax1.set_title(u'Detalle a baja frecuencia')
ax1.set_xlabel('Frecuencia [Hz]')
ax1.set_ylabel('Potencia [db]')
ax1.legend(loc=1)
ax1.grid(linewidth=0.5,linestyle='--')

figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'chirp_normalizada.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

#%% AMPLIFICADOR

carpeta_salida = 'LM324'
subcarpeta_salida = 'Amplificador'
subsubcarpeta_salida = '-5V'

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))    

R2 = 100000
R1 = 4600    

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
dato = 'int16'    
par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50
fs = 44100*8  
duracion = 1
muestras = int(fs*duracion) + int(fs*1)
input_channels = 2
output_channels = 1
amplitud_v_chs_out = [0.02,0.02] #V
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
        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
#        output_signal = signalgen_corrected('square',fr,amp,duration,fs,frec_send,fft_norm,[2,20500])
#        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
        data_out[i,:,j] = output_signal
        
        


# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out'),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in'),data_in)


#%% AMPLIFICADOR FIGURAS

carpeta_salida = 'LM324'
subcarpeta_salida = 'Amplificador'
subsubcarpeta_salida = '-5V'
frec_ini = 500

R2 = 100000
R1 = 4600    

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])
tiempo = np.linspace(0,data_in.shape[1]-1,data_in.shape[1])/fs

med = 0.1
delay = 0.5

input_signal = data_in[0,int(fs*delay):int(fs*delay)+int(fs*med),0]
output_signal = data_in[0,int(fs*delay):int(fs*delay)+int(fs*med),1]
tiempo_signal = tiempo[int(fs*delay):int(fs*delay)+int(fs*med)]

input_signal = input_signal
output_signal = output_signal

fig = plt.figure(dpi=250)
ax = fig.add_axes([.12, .15, .32, .8])
ax1 = ax.twinx()
ax.plot(tiempo_signal,1000*input_signal,'-',color='blue',label='Input',alpha=0.8)
ax1.plot(tiempo_signal,output_signal,'-',color='red',label='Output',alpha=0.8)
ax.legend(loc=1)
ax1.legend(loc=2)
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [s]')
ax.set_ylabel(u'Input [mV]',color='blue')
ax1.set_ylabel(u'Output [V]',color='red')
#ax.set_title('Amplificador con LM324 con seno de ' + str(frec_ini)+ ' Hz y R1='+str(R1/1000)+ ' kOhms y R2=' +str(R2/1000)+ ' kOhms')
ax.set_xlim([0.5,0.505])


#ajuste_lineal_ganancia = np.polyfit(input_signal[int(fs/frec_ini/4):int(fs/frec_ini/4)+int(fs/frec_ini/2)],output_signal[int(fs/frec_ini/4):int(fs/frec_ini/4)+int(fs/frec_ini/2)],1)
ajuste_lineal_ganancia = np.polyfit(input_signal,output_signal,1)

ax2 = fig.add_axes([.65, .15, .32, .8])
ax2.plot(1000*input_signal,output_signal,'-',alpha=0.8,label='Medido')
ax2.plot(1000*input_signal,input_signal*ajuste_lineal_ganancia[0]+ajuste_lineal_ganancia[1],'-',alpha=0.8,label='Ajuste')

ax2.text(0.1,0.8,'Ajuste: ax + b', transform=ax2.transAxes)
ax2.text(0.1,0.75,'a: ' '{:6.3f}'.format(ajuste_lineal_ganancia[0]), transform=ax2.transAxes)
ax2.text(0.1,0.70,'b: ' '{:6.3f}'.format(ajuste_lineal_ganancia[1]), transform=ax2.transAxes)

ax2.legend()
ax2.grid(linestyle='--')
ax2.set_xlabel(u'Input [mv]')
ax2.set_ylabel(u'Output [v]')
#ax2.set_title('Linealidad')

figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'salida_amplificador.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)


print(R2/R1+1)

#%% RESPUESTA AMPLIFICADOR

carpeta_salida = 'LM324'
subcarpeta_salida = 'Amplificador'
subsubcarpeta_salida = 'Respuesta_-5V'

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))


R2 = 100000
R1 = 1451


fs = 44100*8  
duracion = 30
muestras = int(fs*duracion)
input_channels = 2
output_channels = 1
par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50

amplitud_v_chs_out = [0.027,0.027] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
    
amplitud = amplitud_chs[0]   

# Frecuencias bajas
frec_ini = 0
frec_fin = 23000
output_signal = amplitud*signal.chirp(np.arange(muestras)/fs,frec_fin,duracion,frec_ini)
ceros = np.zeros(int(fs*1))
output_signal = np.append(output_signal,ceros,axis=0)
output_signal = np.append(ceros,output_signal,axis=0)
data_out1 = np.zeros([1,output_signal.shape[0],output_channels])
data_out1[0,:,0] = output_signal


offset_correlacion = int(fs*(5))
steps_correlacion = int(fs*(0.1))
data_in1, retardos1 = play_rec(fs,input_channels,data_out1,'si',offset_correlacion,steps_correlacion)


np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out_R2_'+str(R2)+'_R1_'+str(R1)),data_out1)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in_R2_'+str(R2)+'_R1_'+str(R1)),data_in1)


###
#%% Figuras respuesta

carpeta_salida = 'LM324'
subcarpeta_salida = 'Amplificador'
subsubcarpeta_salida = 'Respuesta_-5V'

R2 = 100000
R1s = [271,330,386,464,558,667,775,994,1200,1316,1451,1545,1760,2170,3210,4700,6560,8080,9700,14070,20070,29100,48100,62000,100000]

dato = 'int16'    
fs = 44100*8  
par_level = 100
ind_nivel = par2ind(par_level,parlante_levels)
mic_level = 50

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))


frec_comp = 200
n = 20

frec_comp_bw = [200,21000]
ancho_de_banda = []

frec_comp_ganancia = [200,1000,2000,3500,5000,10000,15000]
ganancia = {}
frec_ind_send_ganancia = {}
for j in range(len(frec_comp_ganancia)):
    ganancia[j] = []

fig_tot = plt.figure(dpi=250)
ax_tot = fig_tot.add_axes([.15, .15, .65, .8])

for i in range(len(R1s)):
    
    
    R1 = R1s[i]
    print(R1)

    data_out1 = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out_R2_'+str(R2)+'_R1_'+str(R1)+'.npy'))
    data_in1 = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in_R2_'+str(R2)+'_R1_'+str(R1)+'.npy'))
    
    
    # Calibracion de los canales
    data_in1[:,:,0] = (data_in1[:,:,0]-calibracion_CH0_seno[1]*2**16)/(calibracion_CH0_seno[0]*2**16)
    data_in1[:,:,1] = (data_in1[:,:,1]-calibracion_CH1_seno[1]*2**16)/(calibracion_CH1_seno[0]*2**16)

    frec_send,fft_send = fft_power_density(data_out1[0,:,0],fs)
    frec_acq,fft_acq_input = fft_power_density(data_in1[0,:,0],fs)
    frec_acq,fft_acq_output = fft_power_density(data_in1[0,:,1],fs)   
        
    frec_ind_acq = np.argmin(np.abs(frec_acq-frec_comp))
    frec_ind_send = np.argmin(np.abs(frec_send-frec_comp))

    
#    fig = plt.figure(dpi=250)
#    ax = fig.add_axes([.15, .15, .32, .8])
#    ax.semilogy(frec_send,fft_acq_output/fft_acq_output[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)
#    ax.semilogy(frec_send,fft_acq_input/fft_acq_input[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
#    ax.semilogy(frec_send,fft_send/fft_send[frec_ind_send],'-', label=u'Send',alpha=0.6,linewidth=2)
#    
#    ax.set_xlim([-1000,28000])
#    ax.set_ylim([1e-3,1e1])
#    ax.set_title(u'FFT de la señal digital, input y output para amplificador LM324')
#    ax.set_xlabel('Frecuencia [Hz]')
#    ax.set_ylabel('Potencia [db]')
#    ax.legend(loc=1)
#    ax.grid(linewidth=0.5,linestyle='--')
#    
#    ax1 = fig.add_axes([.60, .15, .32, .8])
#    ax1.semilogy(frec_send,fft_acq_output/fft_acq_output[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)
#    ax1.semilogy(frec_send,fft_acq_input/fft_acq_input[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
#    ax1.semilogy(frec_send,fft_send/fft_send[frec_ind_send],'-', label=u'Send',alpha=0.6,linewidth=2)
#    
#    ax1.set_xlim([-10,200])
#    ax1.set_ylim([1e-3,1e1])
#    ax1.set_title(u'Detalle a baja frecuencia')
#    ax1.set_xlabel('Frecuencia [Hz]')
#    ax1.set_ylabel('Potencia [db]')
#    ax1.legend(loc=1)
#    ax1.grid(linewidth=0.5,linestyle='--')
#    
#    figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'chirp_R2'+str(R2)+'_R1_'+str(R1)+'.png')
#    fig.savefig(figname, dpi=300)  
#    plt.close(fig)
    
    
    
    fft_norm_input = fft_acq_input/fft_acq_input[frec_ind_send]/(fft_send/fft_send[frec_ind_send])
    fft_norm_output = fft_acq_output/fft_acq_output[frec_ind_send]/(fft_send/fft_send[frec_ind_send])
    fft_norm_norm_output = fft_norm_output/fft_norm_output[frec_ind_send]/(fft_norm_input/fft_norm_input[frec_ind_send])
    
    
#    ## Normalizada
#    fig = plt.figure(dpi=250)
#    ax = fig.add_axes([.15, .15, .32, .8])
#    ax.semilogy(frec_send,fft_norm_input/fft_norm_input[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
#    ax.semilogy(frec_send,fft_norm_output/fft_norm_output[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)
#    
#    ax.set_xlim([-1000,28000])
#    ax.set_ylim([1e-3,1e1])
#    ax.set_title(u'FFT normalizada de la señal input y output para seguidor LM324')
#    ax.set_xlabel('Frecuencia [Hz]')
#    ax.set_ylabel('Potencia [db]')
#    ax.legend(loc=1)
#    ax.grid(linewidth=0.5,linestyle='--')
#    
#    ax1 = fig.add_axes([.60, .15, .32, .8])
#    ax1.semilogy(frec_send,fft_norm_input/fft_norm_input[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
#    ax1.semilogy(frec_send,fft_norm_output/fft_norm_output[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)
#    
#    ax1.set_xlim([-10,200])
#    ax1.set_ylim([1e-3,1e1])
#    ax1.set_title(u'Detalle a baja frecuencia')
#    ax1.set_xlabel('Frecuencia [Hz]')
#    ax1.set_ylabel('Potencia [db]')
#    ax1.legend(loc=1)
#    ax1.grid(linewidth=0.5,linestyle='--')
#    
#    figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'chirp_normalizada_R2'+str(R2)+'_R1_'+str(R1)+'.png')
#    fig.savefig(figname, dpi=300)  
#    plt.close(fig)
    
    
    
    ## Normalizada filtrada
    fft_acq_input_filt = np.convolve(fft_acq_input,np.ones(n)/n,mode='valid')
    fft_acq_output_filt = np.convolve(fft_acq_output,np.ones(n)/n,mode='valid')
    fft_send_filt = fft_send[0:fft_acq_input_filt.shape[0]]
    frec_send_filt = frec_send[0:fft_acq_input_filt.shape[0]]
    
    fft_acq_input_filt = fft_acq_input_filt[::n]
    fft_acq_output_filt= fft_acq_output_filt[::n]
    fft_send_filt = fft_send_filt[::n]
    frec_send_filt = frec_send_filt[::n]
    
    frec_ind_send = np.argmin(np.abs(fft_send_filt-frec_comp))
    
    
    fft_norm_input_filt = fft_acq_input_filt/fft_acq_input_filt[frec_ind_send]/(fft_send_filt/fft_send_filt[frec_ind_send])
    fft_norm_output_filt = fft_acq_output_filt/fft_acq_output_filt[frec_ind_send]/(fft_send_filt/fft_send_filt[frec_ind_send])
    fft_norm_norm_output_filt = fft_norm_output_filt/fft_norm_output_filt[frec_ind_send]/(fft_norm_input_filt/fft_norm_input_filt[frec_ind_send])
    
    
    
    fig = plt.figure(dpi=250)
    ax = fig.add_axes([.15, .15, .32, .8])
    ax.semilogy(frec_send_filt,fft_norm_input_filt/fft_norm_input_filt[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
    ax.semilogy(frec_send_filt,fft_norm_output_filt/fft_norm_output_filt[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)
    
    ax.set_xlim([-1000,25000])
    ax.set_ylim([-30,10])
    #ax.set_title(u'FFT normalizada de la señal input y output para seguidor LM324 - Filtrada')
    ax.set_xlabel('Frecuencia [Hz]')
    ax.set_ylabel('Potencia [db]')
    ax.legend(loc=1)
    ax.grid(linewidth=0.5,linestyle='--')
    
    ax1 = fig.add_axes([.60, .15, .32, .8])
    ax1.semilogy(frec_send_filt,fft_norm_input_filt/fft_norm_input_filt[frec_ind_send],'-', label=u'Input',alpha=0.6,linewidth=2)
    ax1.semilogy(frec_send_filt,fft_norm_output_filt/fft_norm_output_filt[frec_ind_send],'-', label=u'Output',alpha=0.6,linewidth=2)
    
    ax1.set_xlim([-10,200])
    ax1.set_ylim([1e-3,1e1])
    ax1.set_title(u'Detalle a baja frecuencia')
    ax1.set_xlabel('Frecuencia [Hz]')
    ax1.set_ylabel('Potencia [db]')
    ax1.legend(loc=1)
    ax1.grid(linewidth=0.5,linestyle='--')
    
    figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'chirp_normalizada_filtrada_R2'+str(R2)+'_R1_'+str(R1)+'.png')
    fig.savefig(figname, dpi=300)  
    plt.close(fig)
    
    ax_tot.plot(frec_send_filt,10*np.log10(fft_norm_output_filt/fft_norm_output_filt[frec_ind_send]),'-',color=cmap(float(i)/len(R1s)), label=u'R2/R1: ' + '{:6.2f}'.format(R2/R1) ,alpha=0.6,linewidth=2)

    # Ancho de banda
    frec_ind_send_lim_ini = np.argmin(np.abs(frec_send_filt-frec_comp_bw[0]))   
    frec_ind_send_lim_fin = np.argmin(np.abs(frec_send_filt-frec_comp_bw[1])) 
    ind_bw = np.argmin(np.abs(fft_norm_output_filt[frec_ind_send_lim_ini:frec_ind_send_lim_fin]/fft_norm_output_filt[frec_ind_send]-0.5))
    frec_bw = frec_send_filt[frec_ind_send_lim_ini+ind_bw]  
    ancho_de_banda.append(frec_bw)


    # Ganancia
    for j in range(len(frec_comp_ganancia)):
        frec_ind_send_ganancia[j] = np.argmin(np.abs(frec_send_filt-frec_comp_ganancia[j])) 
    
    for j in range(len(frec_comp_ganancia)):
        ganancia[j].append(np.sqrt(fft_acq_output_filt[frec_ind_send_ganancia[j]]/fft_acq_input_filt[frec_ind_send_ganancia[j]]))



ax_tot.set_xlim([-1000,23000])
ax_tot.set_ylim([-30,10])
#ax_tot.set_title(u'FFT normalizada de la señal input y output para seguidor LM324 - Filtrada')
ax_tot.set_xlabel('Frecuencia [Hz]')
ax_tot.set_ylabel('Potencia [db]')
ax_tot.legend(bbox_to_anchor=(1.15, 0.00))
ax_tot.grid(linewidth=0.5,linestyle='--')
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'respuestas_r1.png')
fig_tot.savefig(figname, dpi=300)  

ax_tot.set_ylim([-20,10])
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'respuestas_r1_zoom.png')
fig_tot.savefig(figname, dpi=300)  
plt.close(fig_tot)

ax_tot.set_xlim([-10,2000])
ax_tot.set_ylim([-30,10])
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'respuestas_r1_zoom2.png')
fig_tot.savefig(figname, dpi=300)  
plt.close(fig_tot)




R1s_array = np.asarray(R1s)
ancho_de_banda_array = np.asarray(ancho_de_banda)

fig = plt.figure(dpi=250)
ax = fig.add_axes([.10, .15, .35, .8])
for j in range(len(frec_comp_ganancia)):
    ganancia_array = np.asarray(ganancia[j])
    ajuste_lineal_ganancia = np.polyfit(R2/R1s_array,ganancia_array,1)
    
    print(ajuste_lineal_ganancia[0],ajuste_lineal_ganancia[1])

    ax.plot(R2/R1s_array,ganancia_array,'o',color=cmap(float(j)/len(frec_comp_ganancia)),label=str(frec_comp_ganancia[j]) + ' Hz',markersize=10)
    
#    if j == 0:
#        ax.plot(R2/R1s_array,R2/R1s_array*ajuste_lineal_ganancia[0] + ajuste_lineal_ganancia[1],'--',color=cmap(float(j)/len(frec_comp_ganancia)),label='Ajuste')
#        ax.text(0.1,0.8,'Ajuste: ax + b',color=cmap(float(j)/len(frec_comp_ganancia)), transform=ax.transAxes)
#        ax.text(0.1,0.75,'a: ' '{:6.3f}'.format(ajuste_lineal_ganancia[0]),color=cmap(float(j)/len(frec_comp_ganancia)), transform=ax.transAxes)
#        ax.text(0.1,0.70,'b: ' '{:6.3f}'.format(ajuste_lineal_ganancia[1]),color=cmap(float(j)/len(frec_comp_ganancia)), transform=ax.transAxes)

ax.plot(R2/R1s_array,1 + R2/R1s_array,'--',color='red',label='Ganancia teórica',linewidth=2)

ax.set_xlim([0,400])    
ax.set_ylim([0,400])    
#ax.set_title(u'Ganancia vs R2/R1')
ax.set_xlabel('R2/R1')
ax.set_ylabel('Ganancia Tensión')
ax.legend(loc=2)
ax.grid(linewidth=0.5,linestyle='--')


ax1 = fig.add_axes([.60, .15, .35, .8])
ax1.plot(R2/R1s_array,ancho_de_banda_array,'o',markersize=10)
ax1.axvline(50,linestyle='--',color='red',label='Ancho de banda medición')
#ax1.set_title(u'Ancho de banda vs R2/R1')
ax1.set_xlabel('R2/R1')
ax1.set_ylabel('Ancho de banda [Hz]')
ax1.legend(loc=1)
ax1.grid(linewidth=0.5,linestyle='--')
ax1.set_xlim([0,400])    

figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'ganancia_ancho_de_banda.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



fig = plt.figure(dpi=250)
ax = fig.add_axes([.10, .15, .35, .8])
j = 0

for j in range(len(frec_comp_ganancia)):
    ganancia_array = np.asarray(ganancia[j])
    ax.plot(ancho_de_banda_array,ganancia_array,'o',color=cmap(float(j)/len(frec_comp_ganancia)),label=str(frec_comp_ganancia[j]) + ' Hz',markersize=10)
ax.axvline(20000,linestyle='--',color='red',label='Ancho de banda medición')
   
ax.set_ylim([0,400])     
#ax.set_title(u'Ganancia vs Ancho de banda')
ax.set_xlabel('Ancho de banda [Hz]')
ax.set_ylabel('Ganancia Tensión')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')

j = 0
ganancia_array = np.asarray(ganancia[j])
ax1 = fig.add_axes([.60, .15, .35, .8])
ax1.plot(ganancia_array,ganancia_array*ancho_de_banda_array/1000000,'o',color=cmap(float(j)/len(frec_comp_ganancia)),markersize=10,label=str(frec_comp_ganancia[j]) + ' Hz')
ax1.axvline(50,linestyle='--',color='red',label='Ancho de banda medición')
ax1.set_xlim([0,400])     
#ax1.set_title(u'Ganancia*BW vs Ganancia')
ax1.set_xlabel('Ganancia Tensión')
ax1.set_ylabel('Ganancia*Ancho de banda [MHz]')
ax1.legend(loc=1)
ax1.grid(linewidth=0.5,linestyle='--')

figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'ganancia_ancho_de_banda_1.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

##
## LOGLOG Ajuste ancho de banda de ganacia unitaria

ancho_de_banda_array_lim = ancho_de_banda_array[0:10]
ganancia_array_lim = np.asarray(ganancia[0])
ganancia_array_lim = ganancia_array_lim[0:10]
ancho_de_banda_array_lim_log = np.log10(ancho_de_banda_array_lim)
ganancia_array_lim_log = 10*np.log10(ganancia_array_lim)

ajuste = np.polyfit(ancho_de_banda_array_lim_log, ganancia_array_lim_log, 1)

ancho_de_banda_array_aj = np.array([1000,1.0e7])

fig = plt.figure(dpi=250)
ax = fig.add_axes([.12, .15, .75, .8])
j = 0

#ax.semilogx(ancho_de_banda_array,-20*np.log(ancho_de_banda_array),'--',color='red',label='20 db/decada')

for j in range(len(frec_comp_ganancia)):
    ganancia_array = np.asarray(ganancia[j])
    ax.semilogx(ancho_de_banda_array,10*np.log10(ganancia_array),'o',color=cmap(float(j)/len(frec_comp_ganancia)),label=str(frec_comp_ganancia[j]) + ' Hz',markersize=10)

ax.semilogx(np.array([1e6,2e6]),np.array([0,0]),'--',color='black',alpha=0.5)
ax.semilogx(np.array([10**(-ajuste[1]/ajuste[0]),10**(-ajuste[1]/ajuste[0])]),np.array([-2,2]),'--',color='black',alpha=0.5)
ax.semilogx(ancho_de_banda_array_aj,ajuste[1]+ajuste[0]*np.log10(ancho_de_banda_array_aj),'--',color='red',label='Ajuste 200 Hz')

ax.set_ylim([-10,30])    
ax.set_xlim([1000,1e7])  
ax.annotate('Ancho de banda \nde ganancia unitaria:' + '{:6.3f}'.format(10**(-ajuste[1]/ajuste[0])/1000000) + ' MHz', xy=(10**(-ajuste[1]/ajuste[0])-100000,-0.5), xytext=(10**(-ajuste[1]/ajuste[0])-1350000,-8),arrowprops=dict(arrowstyle="->"))
  
#ax.arrow(10**(-ajuste[1]/ajuste[0])-100000,-0.5,-1000000,-5,'->',color='red',alpha=0.7)
#ax.text(10**(-ajuste[1]/ajuste[0])-1350000,-7,'Ancho de banda de ganancia unitaria')
#ax.text(10**(-ajuste[1]/ajuste[0])-1350000,-8.5,'{:6.3f}'.format(10**(-ajuste[1]/ajuste[0])/1000000) + ' MHz')


ax.text(0.4,0.9,'Ajuste: ax + b', transform=ax.transAxes)
ax.text(0.4,0.85,'a: ' '{:6.2f}'.format(ajuste[0])+ ' dB/decada', transform=ax.transAxes)
ax.text(0.4,0.80,'b: ' '{:6.2f}'.format(ajuste[1])+ ' dB', transform=ax.transAxes)
 
#ax.set_title(u'Ganancia vs Ancho de banda')
ax.set_xlabel('Ancho de banda [Hz]')
ax.set_ylabel('Ganancia Tensión [dB]')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')

figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'ganancia_ancho_de_banda_1_loglog.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)




