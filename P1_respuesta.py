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
import scipy 

from P1_funciones import play_rec
from P1_funciones import signalgen
from P1_funciones import sincroniza_con_trigger

params = {'legend.fontsize': 'x-large',
     #     'figure.figsize': (15, 5),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)




#%%

# Respuesta emisor-receptor METODO CHIRP

fs = 44100*8  
duracion = 30
muestras = int(fs*duracion)
input_channels = 2
output_channels = 2
amplitud = 0.1

# Frecuencias bajas
frec_ini = 0
frec_fin = 23000
output_signal = amplitud*signal.chirp(np.arange(muestras)/fs,frec_fin,duracion,frec_ini)
ceros = np.zeros(int(fs*1))
output_signal = np.append(output_signal,ceros,axis=0)
output_signal = np.append(ceros,output_signal,axis=0)
data_out1 = np.zeros([1,output_signal.shape[0],output_channels])
data_out1[0,:,0] = output_signal

#plt.plot(data_out1[0,:,0])

offset_correlacion = int(fs*(5))
steps_correlacion = int(fs*(0.1))
data_in1, retardos1 = play_rec(fs,input_channels,data_out1,'si',offset_correlacion,steps_correlacion)



#plt.plot(data_out1[0,:,0])
#plt.plot(data_in1[0,:,0]/(2**32))


### Realiza la FFT de la señal enviada y adquirida
paso = 0
ch_send = 0
ch_acq = 0
frec_comp = 10000

fft_send1 = abs(fft.fft(data_out1[paso,:,ch_send]))**2/int(data_out1.shape[1]/2+1)/fs
fft_send1 = fft_send1[0:int(data_out1.shape[1]/2+1)]
fft_acq1 = abs(fft.fft(data_in1[paso,:,ch_acq]))**2/int(data_in1.shape[1]/2+1)/fs
fft_acq1 = fft_acq1[0:int(data_in1.shape[1]/2+1)]

frec_send1 = np.linspace(0,int(data_out1.shape[1]/2),int(data_out1.shape[1]/2+1))
frec_send1 = frec_send1*(fs/2+1)/int(data_out1.shape[1]/2+1)
frec_acq1 = np.linspace(0,int(data_in1.shape[1]/2),int(data_in1.shape[1]/2+1))
frec_acq1 = frec_acq1*(fs/2+1)/int(data_in1.shape[1]/2+1)

frec_ind_acq = np.argmin(np.abs(frec_acq1-frec_comp))
frec_ind_send = np.argmin(np.abs(frec_send1-frec_comp))

# Interpolo para poder normalizar
#fft_acq1_interp = np.interp(frec_send1, frec_acq1, fft_acq1)

carpeta_salida = 'Respuesta'
subcarpeta_salida = 'Chirp'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))    


fft_norm1 = fft_acq1/fft_acq1[frec_ind_send]/(fft_send1/fft_send1[frec_ind_send])
np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'respuesta_potencia_chirp'),fft_norm1)
np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'frecuencia_chirp'),frec_send1)


fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax.semilogy(frec_send1,fft_acq1/fft_acq1[frec_ind_send],'-', label=u'Señal adquirida',alpha=0.7,linewidth=2)
ax.semilogy(frec_send1,fft_send1/fft_send1[frec_ind_send],'-', label=u'Señal enviada',alpha=0.7,linewidth=2)
ax.semilogy(frec_send1,fft_norm1,'-', label=u'Señal normalizada',alpha=0.7,linewidth=2)

ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.set_title('Potencia del conjunto emisor-receptor de la placa de audio de PC')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')

figname = os.path.join(carpeta_salida,subcarpeta_salida, 'chirp.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([-100,500])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'chirp_baja_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([15000,25000])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'chirp_alta_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



fig = plt.figure(figsize=(14, 8), dpi=250)
ax = fig.add_axes([.10, .12, .37, .8])
ax.semilogy(frec_send1,fft_acq1/fft_acq1[frec_ind_send],'-', label=u'Señal adquirida',alpha=0.7,linewidth=2)
ax.semilogy(frec_send1,fft_send1/fft_send1[frec_ind_send],'-', label=u'Señal enviada',alpha=0.7,linewidth=2)
ax.semilogy(frec_send1,fft_norm1,'-', label=u'Señal normalizada',alpha=0.7,linewidth=2)

ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.set_title('Potencia del conjunto emisor-receptor')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')

ax1 = fig.add_axes([.58, .12, .37, .8])
ax1.semilogy(frec_send1,fft_acq1/fft_acq1[frec_ind_send],'-', label=u'Señal adquirida',alpha=0.7,linewidth=2)
ax1.semilogy(frec_send1,fft_send1/fft_send1[frec_ind_send],'-', label=u'Señal enviada',alpha=0.7,linewidth=2)
ax1.semilogy(frec_send1,fft_norm1,'-', label=u'Señal normalizada',alpha=0.7,linewidth=2)

ax1.set_xlim([-100,500])
ax1.set_ylim([1e-3,1e1])
ax1.set_xlabel('Frecuencia [Hz]')
ax1.set_ylabel('Potencia [db]')
ax1.set_title('Detalle baja frecuencia')
ax1.legend(loc=1)
ax1.grid(linewidth=0.5,linestyle='--')

figname = os.path.join(carpeta_salida,subcarpeta_salida, 'chirp_detalle.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)





# Normalizado



fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax.semilogy(frec_send1,fft_norm1,'-',color='blue', label=u'Señal normalizada',alpha=0.7,linewidth=2)
ax.axvline(14.6,linestyle='--',color='red',alpha=0.7, label='Ancho de banda')
ax.axvline(20187,linestyle='--',color='red',alpha=0.7)
ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.set_title('Potencia del conjunto emisor-receptor de la placa de audio de PC. Normalizada con señal enviada. BW: 14.6 Hz - 20187 Hz')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')
plt.show()

figname = os.path.join(carpeta_salida,subcarpeta_salida, 'chirp_normalizada.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([-100,500])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'chirp_baja_frecuencia_normalizada.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([15000,25000])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'chirp_alta_frecuencia_normalizada.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



### TRAZA TEMPORAL
fig = plt.figure(figsize=(14, 8), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax1 = ax.twinx()
ax1.plot(data_out1[0,:,0],linewidth=2,color='blue',alpha=0.7,label=u'Señal enviada')
ax.plot(data_in1[0,:,0],linewidth=2,color='red',alpha=0.7,label=u'Señal adquirida')
ax.set_xlabel('Tiempo [muestra]')
ax1.set_ylabel('Intensidad [a.u.]',color='red')
ax.set_ylabel('Intensidad [a.u.]',color='blue')

ax.set_xlim([1.088*1e7,1.100*1e7])
ax.grid(linestyle='--')
ax.legend(loc=1)
ax1.legend(loc=4)
ax.set_title('Detalle en baja frecuencia de chirp')
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'chirp_baja_tiempo.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



#%%

# Respuesta emisor-receptor METODO RUIDO BLANCO

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

fs = 44100*8  
duracion = 30
muestras = int(fs*duracion)
input_channels = 2
output_channels = 2
amplitud = 0.1

output_signal = amplitud*np.random.rand(muestras)
ceros = np.zeros(int(fs*1))
output_signal = np.append(output_signal,ceros,axis=0)
output_signal = np.append(ceros,output_signal,axis=0)

if output_signal.shape[0]%2 == 1:
    output_signal= output_signal[1::]

## Modulacion para sacarle ruido en frecuencias. Equivalente a hacer un moving average en frecuencias
#t0 = 2
#dt = 0.01    
#largo = output_signal.shape[0]
#x = np.linspace(0,largo/2-1,largo/2)
#
##t0 = int(fs*t0)
##dt = int(fs*dt)
##mod = (-np.arctan((x-t0)/dt)/np.pi*2 +1)/2
##mod = np.append(mod,mod[::-1])
#
#x = np.linspace(0,largo/2-1,largo/2)/largo*duracion
#mod = gaussian(x,1.7,0.3)
#mod = np.append(mod,mod[::-1])
#
#output_signal = output_signal*mod
#plt.plot(output_signal)


data_out2 = np.zeros([1,output_signal.shape[0],output_channels])
data_out2[0,:,1] = output_signal
output_signal = signalgen('sine',1000,amplitud,0.5,fs)  
data_out2[0,0:output_signal.shape[0],0] = output_signal

#plt.plot(data_out2[0,:,1])

data_in2, retardos2 = play_rec(fs,input_channels,data_out2,'si')



plt.plot(data_out2[0,:,1])
plt.plot(data_in2[0,:,1]/(2**32))


### Realiza la FFT de la señal enviada y adquirida
paso = 0
ch_send = 1
ch_acq = 1
frec_comp = 10000

fft_send2 = abs(fft.fft(data_out2[paso,:,ch_send]))**2/int(data_out2.shape[1]/2+1)/fs
fft_send2 = fft_send2[0:int(data_out2.shape[1]/2+1)]
fft_acq2 = abs(fft.fft(data_in2[paso,:,ch_acq]))**2/int(data_in2.shape[1]/2+1)/fs
fft_acq2 = fft_acq2[0:int(data_in2.shape[1]/2+1)]

frec_send2 = np.linspace(0,int(data_out2.shape[1]/2),int(data_out2.shape[1]/2+1))
frec_send2 = frec_send2*(fs/2+1)/int(data_out2.shape[1]/2+1)
frec_acq2 = np.linspace(0,int(data_in2.shape[1]/2),int(data_in2.shape[1]/2+1))
frec_acq2 = frec_acq2*(fs/2+1)/int(data_in2.shape[1]/2+1)

frec_ind_acq = np.argmin(np.abs(frec_acq2-frec_comp))
frec_ind_send = np.argmin(np.abs(frec_send2-frec_comp))

# Interpolo para poder normalizar
#fft_acq1_interp = np.interp(frec_send1, frec_acq1, fft_acq1)

carpeta_salida = 'Respuesta'
subcarpeta_salida = 'RuidoBlanco'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))    

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax.semilogy(frec_send2[::50],fft_acq2[::50]/fft_acq2[frec_ind_send],'-',color='blue', label=u'Señal adquirida',alpha=0.7,linewidth=1)
ax.semilogy(frec_send2[::50],fft_send2[::50]/fft_send2[frec_ind_send],'-',color='red', label=u'Señal enviada',alpha=0.7,linewidth=1)
ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e2])
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.set_title('Potencia del conjunto emisor-receptor de la placa de audio de PC')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')

figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruidoblanco.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([-100,500])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruidoblanco_baja_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([15000,25000])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruidoblanco_alta_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)


# Normalizado
fft_norm2 = fft_acq2/fft_acq2[frec_ind_send]/(fft_send2/fft_send2[frec_ind_send])

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax.semilogy(frec_send2,fft_norm2,'-',color='blue', label=u'Señal normalizada',alpha=0.7,linewidth=2)
ax.axvline(14.6,linestyle='--',color='red',alpha=0.7, label='Ancho de banda')
ax.axvline(20187,linestyle='--',color='red',alpha=0.7)
ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.set_title('Potencia del conjunto emisor-receptor de la placa de audio de PC. Normalizada con señal enviada. BW: 14.6 Hz - 20187 Hz')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')
plt.show()

figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruidoblanco_normalizada.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([-100,500])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruidoblanco_baja_frecuencia_normalizada.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([15000,25000])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ruidoblanco_alta_frecuencia_normalizada.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)




#%%
## RESPUESTA EMISOR-RECEPTOR METODO BARRIDO DE FRECUENCIAS

fs = 44100*8  
duracion = 5
muestras = int(fs*duracion)
input_channels = 2
output_channels = 1
amplitud = 0.1

frecs_ini = [0,100,1000,18000,20000]
frecs_fin = [100,1000,18000,20000,23000]
pasos_rangos = [20,20,30,20,20]

data_out = np.zeros([sum(pasos_rangos),muestras,1])
k = 0
frecs_finales = np.array([])
for i in range(len(pasos_rangos)):
    
    frec_ini = frecs_ini[i]
    frec_fin = frecs_fin[i]
    pasos = pasos_rangos[i]
    
    delta_frec = (frec_fin-frec_ini)/(pasos+1)
    
    for j in range(pasos):
        
        fr = frec_ini + j*delta_frec        
        output_signal = signalgen('sine',fr,amplitud,duracion,fs)
        
        data_out[k,:,0] = output_signal
        
        frecs_finales = np.append(frecs_finales,fr)
        
        k = k + 1
    
    
# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion)



#%%
# Graficos

delay = int(fs*0.5)
muestras_analisis = int(fs*3)

iteraciones = 10
amp_salida_max = np.array([])
amp_salida_min = np.array([])

for i in range(data_in.shape[0]):
    
    data_in_i = data_in[i,delay:delay+muestras_analisis,0]
    data_out_i = data_out[i,delay:delay+muestras_analisis,0]
    
    if np.isnan(data_in_i[0]):
        amp_salida_max = np.append(amp_salida_max,np.NaN)
        amp_salida_min = np.append(amp_salida_min,np.NaN)      
        continue
    
    periodo = int(1/frecs_finales[i]*fs)
    
    amp_maxis = 0
    amp_minis = 0
    for j in range(iteraciones):       

        amp_maxis = amp_maxis + np.max(data_in_i[j*periodo:(j+1)*periodo])
        amp_minis = amp_minis + np.min(data_in_i[j*periodo:(j+1)*periodo])    
           
    
    amp_salida_max = np.append(amp_salida_max,amp_maxis)
    amp_salida_min = np.append(amp_salida_min,amp_minis)
    
    


ind_frec = np.argmin(np.abs(frecs_finales-10000))

pot_salida_max = amp_salida_max**2/amp_salida_max[ind_frec]**2
pot_salida_min = amp_salida_min**2/amp_salida_min[ind_frec]**2




carpeta_salida = 'Respuesta'
subcarpeta_salida = 'Barrido'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))    

fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax.semilogy(frecs_finales,pot_salida_max,'-',color='blue', label=u'Señal adquirida',alpha=0.7,linewidth=2)
ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
ax.set_title(u'Potencia de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.set_title('Potencia del conjunto emisor-receptor de la placa de audio de PC. Método barrido.')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')
plt.show()

figname = os.path.join(carpeta_salida,subcarpeta_salida, 'barrido.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([-100,500])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'barrido_baja_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([15000,25000])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'barrido_alta_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



#%%
## COMPARACION POTENCIA EMISOR-RECEPTOR: METODO BARRIDO DE FRECUENCIAS Y CHIRP

carpeta_salida = 'Respuesta'
subcarpeta_salida = 'ComparacionChirp'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida)) 


fig = plt.figure(figsize=(14, 8), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax.semilogy(frec_send1,fft_norm1,'-',color='blue', label=u'Potencia por chirp',alpha=0.7,linewidth=2) # por chirp
ax.semilogy(frecs_finales,pot_salida_max,'o',color='red', label=u'Potencia por barrido',alpha=0.7,linewidth=2) # barrido

ax.axvline(14.6,linestyle='--',color='red',alpha=0.7, label='Ancho de banda')
ax.axvline(20187,linestyle='--',color='red',alpha=0.7)
ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.set_title('Potencia del conjunto emisor-receptor. Comparación método chirp y barrido. BW: 14.6 Hz - 20187 Hz')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')
plt.show()


figname = os.path.join(carpeta_salida,subcarpeta_salida, 'comparacion.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([-100,500])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'comparacion_baja_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([15000,25000])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'comparacion_alta_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



fig = plt.figure(figsize=(14, 8), dpi=250)
ax = fig.add_axes([.10, .12, .37, .8])
ax.semilogy(frec_send1,fft_norm1,'-',color='blue', label=u'Potencia por chirp',alpha=0.7,linewidth=2) # por chirp
ax.semilogy(frecs_finales,pot_salida_max,'o',color='red', label=u'Potencia por barrido',alpha=0.7,linewidth=2) # barrido

ax.axvline(14.6,linestyle='--',color='red',alpha=0.7, label='Ancho de banda')
ax.axvline(20187,linestyle='--',color='red',alpha=0.7)
ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.set_title('Potencia del conjunto emisor-receptor. Comparación método chirp y barrido. BW: 14.6 Hz - 20187 Hz')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')

ax1 = fig.add_axes([.58, .12, .37, .8])
ax1.semilogy(frec_send1,fft_norm1,'-',color='blue', label=u'Potencia por chirp',alpha=0.7,linewidth=2) # por chirp
ax1.semilogy(frecs_finales,pot_salida_max,'o',color='red', label=u'Potencia por barrido',alpha=0.7,linewidth=2) # barrido

ax1.set_xlim([-100,500])
ax1.set_ylim([1e-3,1e1])
ax1.set_xlabel('Frecuencia [Hz]')
ax1.set_ylabel('Potencia [db]')
ax1.set_title('Detalle baja frecuencia')
ax1.legend(loc=1)
ax1.grid(linewidth=0.5,linestyle='--')

figname = os.path.join(carpeta_salida,subcarpeta_salida, 'comparacion_detalle.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

#%%
## COMPARACION POTENCIA EMISOR-RECEPTOR: METODO BARRIDO DE FRECUENCIAS Y RUIDO BLANCO

carpeta_salida = 'Respuesta'
subcarpeta_salida = 'ComparacionRuidoBlanco'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida)) 


fig = plt.figure(figsize=(14, 7), dpi=250)
ax = fig.add_axes([.12, .12, .75, .8])
ax.semilogy(frec_send2,fft_norm2,'-',color='blue', label=u'Potencia por ruido blanco',alpha=0.7,linewidth=2) # por chirp
ax.semilogy(frecs_finales,pot_salida_max,'o',color='red', label=u'Potencia por barrido',alpha=0.7,linewidth=2) # barrido

ax.axvline(14.6,linestyle='--',color='red',alpha=0.7, label='Ancho de banda')
ax.axvline(20187,linestyle='--',color='red',alpha=0.7)
ax.set_xlim([-1000,28000])
ax.set_ylim([1e-3,1e1])
ax.set_title(u'FFT de la señal enviada y adquirida')
ax.set_xlabel('Frecuencia [Hz]')
ax.set_ylabel('Potencia [db]')
ax.set_title('Potencia del conjunto emisor-receptor de la placa de audio de PC. Comparación método rudio blanco y barrido. BW: 14.6 Hz - 20187 Hz')
ax.legend(loc=1)
ax.grid(linewidth=0.5,linestyle='--')
plt.show()



figname = os.path.join(carpeta_salida,subcarpeta_salida, 'comparacion.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([-100,500])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'comparacion_baja_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

ax.set_xlim([15000,25000])
figname = os.path.join(carpeta_salida,subcarpeta_salida, 'comparacion_alta_frecuencia.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)