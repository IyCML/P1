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
from P1_funciones import completa_con_ceros

params = {'legend.fontsize': 14,
          'figure.figsize': (14, 9),
         'axes.labelsize': 24,
         'axes.titlesize':18,
         'font.size':18,
         'xtick.labelsize':24,
         'ytick.labelsize':24}
pylab.rcParams.update(params)





#%%

input_channels = 2
output_channels = 2
amplitud = 0.1
fr1 = 1000
fr2 = 1000
pasos_por_duracion = 10

super_duraciones = []
super_chunk_output_size = []
super_chunk_input_size = []
super_retardos_totales = []
super_fs = []


carpeta_salida = 'Delay'
subcarpeta_salida = 'Frec_sampleo4'

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)

if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))    

for k in range(1,9):

    fs = 44100*1*k  
    super_fs.append(fs)
    print('Fs: ',fs)
    
    duraciones = np.array([])
    duraciones = np.append(duraciones,np.linspace(0.5,240/k,10))
    
    retardos_totales = []
    chunk_output_size = []
    chunk_input_size = []
    
    for i in range(duraciones.shape[0]):
        
        duracion = duraciones[i]
        muestras = int(fs*duracion)
        
        print('Duracion: ',duracion)
            
        data_out = np.zeros([pasos_por_duracion,muestras,output_channels],dtype=np.float32)
        for j in range(pasos_por_duracion):
            
            output_signal = signalgen('sine',fr1,amplitud,0.5,fs)       
            data_out[j,0:output_signal.shape[0],0] = output_signal
            
            output_signal = signalgen('sine',fr2,amplitud,duracion,fs) 
            data_out[j,:,1] = output_signal
    
    
        data_in, retardos = play_rec(fs,input_channels,data_out,'no')
        
        chunk_output_size.append(data_out.shape[1]*4*output_channels*np.dtype(np.float32).itemsize)
        chunk_input_size.append(data_in.shape[1]*output_channels*np.dtype(np.float32).itemsize)  
        
        data_in_corrected, retardos = sincroniza_con_trigger(data_out,data_in)
    
        retardos_totales.append(retardos)


    np.save(os.path.join(carpeta_salida,subcarpeta_salida,'duraciones_'+str(k)),duraciones)
    np.save(os.path.join(carpeta_salida,subcarpeta_salida,'chunk_output_size_'+str(k)),chunk_output_size)
    np.save(os.path.join(carpeta_salida,subcarpeta_salida,'chunk_input_size_'+str(k)),chunk_input_size)
    np.save(os.path.join(carpeta_salida,subcarpeta_salida,'retardos_totales_'+str(k)),retardos_totales)

    
    super_duraciones.append(duraciones)
    super_chunk_output_size.append(chunk_output_size)
    super_chunk_input_size.append(chunk_input_size)
    super_retardos_totales.append(retardos_totales)


    
    
np.save(os.path.join(carpeta_salida,subcarpeta_salida,'super_duraciones'),super_duraciones)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,'super_chunk_output_size'),super_chunk_output_size)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,'super_chunk_input_size'),super_chunk_input_size)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,'super_retardos_totales'),super_retardos_totales)



plt.plot(data_out[0,:,1]*1e10)
plt.plot(data_in[0,:,1])



#%% ANALISIS DELAY

carpeta_salida = 'Delay'
subcarpeta_salida = 'Frec_sampleo4'

super_retardos_totales = np.load(os.path.join(carpeta_salida,subcarpeta_salida,'super_retardos_totales.npy'))
super_duraciones = np.load(os.path.join(carpeta_salida,subcarpeta_salida,'super_duraciones.npy'))
super_chunk_output_size = np.load(os.path.join(carpeta_salida,subcarpeta_salida,'super_chunk_output_size.npy'))
super_chunk_input_size = np.load(os.path.join(carpeta_salida,subcarpeta_salida,'super_chunk_input_size.npy'))


ret_por_frec_sampleo = np.zeros([8,4])
frecuencias_sampleo = np.array([])


for k in range(8):
    
    frec_sampleo = 44100*(k+1)  
    frecuencias_sampleo = np.append(frecuencias_sampleo,frec_sampleo)
    
    fig = plt.figure(dpi=250)
    ax = fig.add_axes([.15, .15, .75, .8])     
    
    ret = super_retardos_totales[k]  
    dura = super_duraciones[k]
    chunk_size_in = super_chunk_input_size[k]
    chunk_size_out = super_chunk_output_size[k]/4
    for i in range(len(ret)):
        ret[i][ret[i]<0] = np.NaN
        ax.plot(ret[i]/frec_sampleo*1000,'o-',color=cmap(float(i)/10),label=u'Tamaño chunk in:' + '{:6.2f}'.format(chunk_size_in[i]/1024/1024) + ' Mbytes - Tamaño chunk out: ' + '{:6.2f}'.format(chunk_size_out[i]/1024/1024) + ' Mbytes')
        
    ax.set_ylim([-100,500])
    ax.legend()
    ax.grid(linestyle='--')
    ax.set_xlabel('Corrida N°')
    ax.set_ylabel('Retardo [ms]')
    ax.set_title('Retardo para distintos tamaños de chunks y frecuencia de sampleo '+ '{:6.2f}'.format(frec_sampleo/1000) + ' kHz')
    figname = os.path.join(carpeta_salida,subcarpeta_salida, 'frec_'+str(k)+'.png')
    fig.savefig(figname, dpi=300)  
    plt.close(fig)

    for j in range(4):
        reti = ret[2*j]
        ret_por_frec_sampleo[k,j] = reti[0]/frec_sampleo*1000
        



#%%

input_channels = 2
output_channels = 2
amplitud = 0.1
fr1 = 1000
pasos_por_duracion = 10
tiempo_de_latencia = 0.1015873015873015
fs = 44100*4 
duracion = 4
muestras = int(fs*duracion)
frecs = np.linspace(500,15000,15)

carpeta_salida = 'Delay'
subcarpeta_salida = 'Frec_senal4'

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)

if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))    

frecuencias_totales = []
retardos_totales = []
chunk_output_size = []
chunk_input_size = []
    
for i in range(frecs.shape[0]):
    
    fr2 = frecs[i]       
        
    chunk_output_size.append(muestras*4*output_channels*np.dtype(np.float32).itemsize)
    chunk_input_size.append((muestras + int(fs*0.6) + int(fs*tiempo_de_latencia))*output_channels*np.dtype(np.float32).itemsize)
        
    data_out = np.zeros([pasos_por_duracion,muestras,output_channels],dtype=np.float32)
    for j in range(pasos_por_duracion):
            
        output_signal = signalgen('sine',fr1,amplitud,0.5,fs)       
        data_out[j,0:output_signal.shape[0],0] = output_signal
            
        output_signal = signalgen('sine',fr2,amplitud,duracion,fs) 
        data_out[j,:,1] = output_signal
    
    
    data_in, retardos = play_rec(fs,input_channels,data_out,'no')
    data_in_corrected, retardos = sincroniza_con_trigger(data_out,data_in)
    
    retardos_totales.append(retardos)
    frecuencias_totales.append(fr2)

np.save(os.path.join(carpeta_salida,subcarpeta_salida,'frecuencias'),frecuencias_totales)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,'chunk_output_size'),chunk_output_size)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,'chunk_input_size'),chunk_input_size)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,'retardos_totales'),retardos_totales)

    
#%% ANALISIS DELAY 2


carpeta_salida = 'Delay'
subcarpeta_salida = 'Frec_senal4'

frecuencias_totales = np.load(os.path.join(carpeta_salida,subcarpeta_salida,'frecuencias.npy'))
chunk_output_size = np.load(os.path.join(carpeta_salida,subcarpeta_salida,'chunk_output_size.npy'))
chunk_input_size = np.load(os.path.join(carpeta_salida,subcarpeta_salida,'chunk_input_size.npy'))
retardos_totales = np.load(os.path.join(carpeta_salida,subcarpeta_salida,'retardos_totales.npy'))

frec_sampleo = 44100*4  

fig = plt.figure(dpi=250)
ax = fig.add_axes([.12, .12, .65, .8])
    
ret = retardos_totales  
frecs = frecuencias_totales
for i in range(len(ret)):
    ret[i][ret[i]<0] = np.NaN
    ax.plot(ret[i]/frec_sampleo*1000,'o-',color=cmap(float(i)/15),label=u'Frec señal:' + '{:6.2f}'.format(frecs[i]/1000) + ' kHz' )
        
ax.set_ylim([100,150])
ax.legend(bbox_to_anchor=(1.02, 1.00))
ax.grid(linestyle='--')
ax.set_xlabel('Corrida N°')
ax.set_ylabel('Retardo [ms]')
ax.set_title('Retardo para distintas frecuencias enviadas y frecuencia de sampleo '+ '{:6.2f}'.format(frec_sampleo/1000) + ' kHz. Tamaño chunk: ' '{:6.2f}'.format(chunk_output_size[0]/1024/1024)+ ' Mbytes')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'frec.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



#%%
# EJEMPLO DE ADQUISICION

from P1_funciones import sincroniza_con_trigger1


windows_nivel = np.array([10,20,30,40,50,60,70,80,90,100])
tension_rms_v_ch0 = np.array([0.050, 0.142, 0.284, 0.441, 0.678, 0.884, 1.143, 1.484, 1.771, 2.280])
amplitud_v_ch0 = tension_rms_v_ch0*np.sqrt(2)
tension_rms_v_ch1 = np.array([0.050, 0.146, 0.291, 0.451, 0.693, 0.904, 1.170, 1.518, 1.812, 2.330])
amplitud_v_ch1 = tension_rms_v_ch1*np.sqrt(2)

amplitud_v_chs = np.array([amplitud_v_ch0,amplitud_v_ch1])


dato = 'int16' 

carpeta_salida = 'Delay'
subcarpeta_salida = 'ejemplo'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
ind_nivel = 6
mic_level = 70
fs = 44100*8  
duracion = 0.3
muestras = int(fs*duracion)
input_channels = 2
output_channels = 2
amplitud_v_chs_out = [1.0,1.0] #V
amplitud_chs = []
for i in range(output_channels):
    amplitud_chs.append(amplitud_v_chs_out[i]/amplitud_v_chs[i,ind_nivel])
    
frec_ini = 71
frec_fin = 71
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
    data_out[i,0:int(fs*0.105),0] = output_signal[0:int(fs*0.105)]
        
    output_signal = signalgen('ramp',fr,amp,duration,fs)
    data_out[i,:,1] = output_signal

data_in, retardos = play_rec(fs,input_channels,data_out,'no',dato=dato)
data_in_corrected, retardos, corr = sincroniza_con_trigger1(data_out,data_in)


#%%

t_out = np.arange(data_out.shape[1])/fs
t_in = np.arange(data_in.shape[1])/fs
t_in_corrected = np.arange(data_in_corrected.shape[1])/fs
t_corr = np.arange(corr.shape[0])/fs


fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .37])
ax1 = fig.add_axes([.15, .56, .75, .37])
ax.plot(t_out,data_out[0,:,1],color='red',alpha=0.8,label='CH1')
ax1.plot(t_out,data_out[0,:,0],color='blue',alpha=0.8,label='CH0')
ax.legend()
ax1.legend()
ax.grid(linestyle='--')
ax1.grid(linestyle='--')
ax.set_xlabel('Tiempo [seg]')
ax.set_ylabel('Amplitud [u.a.]')
ax1.set_ylabel('Amplitud [u.a.]')
ax1.set_title('Señal sintética enviada')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'senal_sintetica.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .37])
ax1 = fig.add_axes([.15, .56, .75, .37])
ax.plot(t_in,data_in[0,:,1],color='red',alpha=0.8,label='CH1')
ax1.plot(t_in,data_in[0,:,0],color='blue',alpha=0.8,label='CH0')
ax.axvline(retardos[0]/fs,linestyle='--',label='retardo')
ax1.axvline(retardos[0]/fs,linestyle='--',label='retardo')
ax.legend()
ax1.legend()
ax.grid(linestyle='--')
ax1.grid(linestyle='--')
ax.set_xlabel('Tiempo [seg]')
ax.set_ylabel('Amplitud [u.a.]')
ax1.set_ylabel('Amplitud [u.a.]')
ax1.set_title('Señal adquirida sin corregir retardo')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'senal_adquirida.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .37])
ax1 = fig.add_axes([.15, .56, .75, .37])
ax.plot(t_in_corrected,data_in_corrected[0,:,1],color='red',alpha=0.8,label='CH1')
ax1.plot(t_in_corrected,data_in_corrected[0,:,0],color='blue',alpha=0.8,label='CH0')
ax.legend()
ax1.legend()
ax.grid(linestyle='--')
ax1.grid(linestyle='--')
ax.set_xlabel('Tiempo [seg]')
ax.set_ylabel('Amplitud [u.a.]')
ax1.set_ylabel('Amplitud [u.a.]')
ax1.set_title('Señal adquirida con retardo corregido')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'senal_adquirida_corregida.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)


ind_max = np.argmax(corr)

fig = plt.figure(dpi=250)
ax = fig.add_axes([.17, .15, .75, .8])     
ax.plot(t_corr,corr,color='red',alpha=0.8,label=u'Correlación cruzada CH0')
ax.axvline(t_corr[len(t_corr)-1]/2,linewidth=2,linestyle='--',color='blue',label=u'duración/2',alpha=0.8)
ax.axvline(t_corr[ind_max],linewidth=2,linestyle='--',color='green',label=u'máximo correlación',alpha=0.8)
ax.text(t_corr[ind_max]-0.11,np.max(corr)*0.95,'Retardo: ', horizontalalignment='left')
ax.text(t_corr[ind_max]-0.11,np.max(corr)*0.87,str(int(1000*retardos[0]/fs)) + ' ms' , horizontalalignment='left')
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel('Tiempo [seg]')
ax.set_ylabel('Amplitud [u.a.]')
ax.set_title('Correlación cruzada entre señal digital de salida y señal adquirida del CH0')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'correlacion_cruzada.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)
