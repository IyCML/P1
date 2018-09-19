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


from P1_funciones import play_rec
from P1_funciones import signalgen
from P1_funciones import signalgen_corrected
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

windows_nivel = np.array([10,20,30,40,50,60,70,80,90,100])
tension_rms_v_ch0 = np.array([0.050, 0.142, 0.284, 0.441, 0.678, 0.884, 1.143, 1.484, 1.771, 2.280])
amplitud_v_ch0 = tension_rms_v_ch0*np.sqrt(2)
tension_rms_v_ch1 = np.array([0.050, 0.146, 0.291, 0.451, 0.693, 0.904, 1.170, 1.518, 1.812, 2.330])
amplitud_v_ch1 = tension_rms_v_ch1*np.sqrt(2)

amplitud_v_chs = np.array([amplitud_v_ch0,amplitud_v_ch1])

#%%

def func_exp(x, a, b, c):
    return a * np.exp(x/b) + c

#%%
diodo = '1N4148'
carpeta_salida = 'CurvaDiodo'
subcarpeta_salida = 'Curvas'
subsubcarpeta_salida = diodo

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     

if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))       

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
dato = 'int16'    
ind_nivel = 6
mic_level = 70
fs = 44100*8  
duracion = 5
muestras = int(fs*duracion) + int(fs*1)
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

#%%
diodo = '1N4007'
carpeta_salida = 'CurvaDiodo'
subcarpeta_salida = 'Curvas'
subsubcarpeta_salida = diodo

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1' + '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])


#plt.plot(data_in[0,:,0])
#plt.plot(data_in[0,:,1])


resistencia = 84
temp = 20
delay = 3
med = 1
offset = 0.175 #R150

caida_tot = data_in[0,int(fs*delay):int(fs*(delay+med)),0]
caida_res = data_in[0,int(fs*delay):int(fs*(delay+med)),1] +offset#+ np.max(data_in[0,int(fs*delay):int(fs*(delay+med)),1])
tiempo = np.arange(data_in.shape[1])/fs
tiempo = tiempo[int(fs*delay):int(fs*(delay+med))]
caida_diodo = caida_tot - caida_res
i_res = caida_res/resistencia


# Seno creciente y decreciente
ind_cre = np.diff(data_out[0,int(fs*delay):int(fs*(delay+med)),0]) < 0
ind_dec = np.diff(data_out[0,int(fs*delay):int(fs*(delay+med)),0]) > 0

#ole = data_out[0,int(fs*delay):int(fs*(delay+med))-1,0]
#plt.plot(ole[ind_dec],'.')

caida_diodo_cre = caida_diodo[1:]
caida_diodo_cre = caida_diodo_cre[ind_cre]
caida_diodo_dec = caida_diodo[1:]
caida_diodo_dec = caida_diodo_dec[ind_dec]

i_res_cre = i_res[:-1]
i_res_cre = i_res_cre[ind_cre]
i_res_dec = i_res[:-1]
i_res_dec = i_res_dec[ind_dec]

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.plot(caida_diodo_cre,i_res_cre*1000,'.',label='Flanco creciente',alpha=0.8)
ax.plot(caida_diodo_dec,i_res_dec*1000,'.',label='Flanco decreciente',alpha=0.8)
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tensión diodo [V]')
ax.set_ylabel(u'Corriente diodo [mA]')
ax.set_xlim([-1.5,1])
ax.set_ylim([-1,11])
ax.set_title('Curva del diodo '+diodo+' utilizando un seno de '+str(frec_ini)+' Hz')
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'curva_diodo_'+diodo+'_'+str(resistencia)+'_'+str(temp)+'C_'+str(frec_ini)+'hz.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

# Ajuste de curva
Is = 1.0*1e-12
K = 1.38064852e-23
Q = 1.6021766208e-19
temp_k = temp + 273.2
Vt = K*temp_k/Q
n = 1.0

# Ajuste creciente
caida_diodo_cre_uno = caida_diodo_cre[0:int(fs/(frec_ini*2))]
i_res_cre_uno = i_res_cre[0:int(fs/(frec_ini*2))]
guess = np.array([Is, Vt/n, Is])
popt_cre, pcov = curve_fit(func_exp, caida_diodo_cre_uno, i_res_cre_uno,guess)

# Ajuste decreciente
caida_diodo_dec_uno = caida_diodo_dec[int(fs/(frec_ini*4)):+int(fs/(frec_ini*4))+int(fs/(frec_ini*2))]
i_res_dec_uno = i_res_dec[int(fs/(frec_ini*4)):+int(fs/(frec_ini*4))+int(fs/(frec_ini*2))]
guess = np.array([Is, Vt/n, Is])
popt_dec, pcov = curve_fit(func_exp, caida_diodo_dec_uno, i_res_dec_uno,guess)

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.plot(caida_diodo_cre_uno,i_res_cre_uno*1000,'.',label='Flanco creciente',alpha=0.7)
#ax.plot(caida_diodo_dec_uno,i_res_dec_uno*1000,'.',label='Flanco decreciente',alpha=0.7)
ax.plot(caida_diodo_cre_uno,func_exp(caida_diodo_cre_uno, *popt_cre)*1000,'--',label='Ajuste Flanco creciente',alpha=0.9)
#ax.plot(caida_diodo_dec_uno,func_exp(caida_diodo_dec_uno, *popt_dec)*1000,'--',label='Ajuste Flanco decreciente',alpha=0.7)
ax.text(0.1,0.8,'Ajuste: a*exp(x/b) + c', transform=ax.transAxes)
ax.text(0.1,0.75,'a: ' '{:6.2e}'.format(popt_cre[0]) + ' [A]', transform=ax.transAxes)
ax.text(0.1,0.70,'b: ' '{:6.2e}'.format(popt_cre[1]) + ' [V]', transform=ax.transAxes)
ax.text(0.1,0.65,'c: ' '{:6.2e}'.format(popt_cre[2]) + ' [A]', transform=ax.transAxes)
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tensión diodo [V]')
ax.set_ylabel(u'Corriente diodo [mA]')
ax.set_xlim([-1.6,1])
ax.set_ylim([-1,11])
ax.set_title('Curva del diodo '+diodo+' utilizando un seno de '+str(frec_ini)+' Hz y ajuste')
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'ajuste_diodo_'+diodo+'_'+str(resistencia)+'_'+str(temp)+'C_'+str(frec_ini)+'hz.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.plot(tiempo,caida_tot,'-',label=u'Tensión diodo + desistencia',alpha=0.8,linewidth=2)
ax.plot(tiempo,caida_diodo,'-',label=u'Tensión diodo',alpha=0.8,linewidth=2)
ax.plot(tiempo,caida_res,'-',label=u'Tensión resistencia',alpha=0.8,linewidth=2)
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [seg]')
ax.set_ylabel(u'Tensión [V]')
ax.set_xlim([delay+0.1,delay+0.11])
ax.set_ylim([-1.5,1.5])
ax.set_title(u'Caida de tensión en diodo y resistencia '+diodo+' utilizando un seno de '+str(frec_ini)+' Hz')
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'caida_diodo_res_'+diodo+'_'+str(resistencia)+'_'+str(temp)+'C_'+str(frec_ini)+'hz.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

###
# Corrección de offset

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1' + '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])


caida_tot = data_in[0,int(fs*delay):int(fs*(delay+med)),0]
caida_res = data_in[0,int(fs*delay):int(fs*(delay+med)),1]#+ np.max(data_in[0,int(fs*delay):int(fs*(delay+med)),1])


fft1 = np.abs(fft.fft(caida_res))
fft2 = np.abs(fft.fft(caida_res+0.175))
fft1 = fft1[0:int(len(fft1)/2)+1]
fft2 = fft2[0:int(len(fft2)/2)+1]

frec = np.arange(0,len(fft1))/len(fft1)*fs/2

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .32, .8])
ax.plot(tiempo,caida_res,'-',label=u'Tensión resistencia medida',alpha=0.8,linewidth=2)
ax.plot(tiempo,caida_res+0.175,'-',label=u'Tensión resistencia corregida',alpha=0.8,linewidth=2)
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [seg]')
ax.set_ylabel(u'Tensión [V]')
ax.set_xlim([delay+0.1,delay+0.11])
ax.set_ylim([-1.0,1.0])

ax1 = fig.add_axes([.60, .15, .32, .8])
ax1.plot(frec,fft1,'-',label=u'FFT tensión medida',alpha=0.8,linewidth=2)
ax1.plot(frec,fft2,'-',label=u'FFT tensión corregida',alpha=0.5,linewidth=2)
ax1.set_xlim([-200,2000])
ax1.set_xlabel(u'Frecuencia [Hz]')
ax1.set_ylabel(u'FFT [u.a.]')
ax1.legend()
ax1.grid(linestyle='--')
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'caida_diodo_res_'+diodo+'_'+str(resistencia)+'_'+str(temp)+'C_'+str(frec_ini)+'hz_fft.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)



delay = 0
med = 1
offset = 0.0 #R150

caida_tot = data_in[0,int(fs*delay):int(fs*(delay+med)),0]
caida_res = data_in[0,int(fs*delay):int(fs*(delay+med)),1] +offset#+ np.max(data_in[0,int(fs*delay):int(fs*(delay+med)),1])
tiempo = np.arange(data_in.shape[1])/fs
tiempo = tiempo[int(fs*delay):int(fs*(delay+med))]

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.plot(tiempo,caida_tot,'-',label=u'Tensión Diodo + Resistencia',alpha=0.8,linewidth=2)
ax.plot(tiempo,caida_diodo,'-',label=u'Tensión diodo',alpha=0.8,linewidth=2)
ax.plot(tiempo,caida_res,'-',label=u'Tensión resistencia',alpha=0.8,linewidth=2)
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [seg]')
ax.set_ylabel(u'Tensión [V]')
ax.set_xlim([delay+0.0,delay+0.10])
ax.set_ylim([-1.5,1.5])
ax.set_title(u'Caida de tensión en diodo y resistencia '+diodo+' utilizando un seno de '+str(frec_ini)+' Hz. Sin corrección de offset.')
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'caida_diodo_res_'+diodo+'_'+str(resistencia)+'_'+str(temp)+'C_'+str(frec_ini)+'hz_sin_corregir_offset.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)

fac = 4.78/4.35

t1 = (20+273.2)*fac - 273.2


#%% Estudio de offset

data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1' + '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])
tiempo = np.arange(data_in.shape[1])/fs

delay = 0
med = 1
offset = 0.0 #R150

caida_tot = data_in[0,:,0] 
caida_res = data_in[0,:,1] 


caida_offset = caida_res[np.arange(0,int(fs*0.2),int(fs/frec_ini))+500]
tiempo_offset = tiempo[np.arange(0,int(fs*0.2),int(fs/frec_ini))+500]

popt_fit, pcov = curve_fit(func_exp, tiempo_offset, caida_offset)



fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
ax.plot(tiempo,caida_tot,'-',label=u'Tensión Diodo + Resistencia',alpha=0.8,linewidth=2)
ax.plot(tiempo,caida_res ,'-',label=u'Tensión resistencia',alpha=0.8,linewidth=2)
ax.plot(tiempo_offset,func_exp(tiempo_offset, *popt_fit),'--',color='red',label='Ajuste caida')

ax.text(0.7,0.9,'Ajuste: a*exp(x/b) + c', transform=ax.transAxes)
ax.text(0.7,0.85,'a: ' '{:6.2e}'.format(popt_fit[0]) + ' [V]', transform=ax.transAxes)
ax.text(0.7,0.80,'b: ' '{:6.2e}'.format(-popt_fit[1]) + ' [sec]', transform=ax.transAxes)
ax.text(0.7,0.75,'c: ' '{:6.2e}'.format(popt_fit[2]) + ' [V]', transform=ax.transAxes)

ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [seg]')
ax.set_ylabel(u'Tensión [V]')
ax.set_xlim([delay+0.0,delay+0.1])
ax.set_ylim([-1.5,1.5])
ax.set_title(u'Caida de tensión en diodo y resistencia '+diodo+' utilizando un seno de '+str(frec_ini)+' Hz. Sin corrección de offset.')
figname = os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'caida_diodo_res_'+diodo+'_'+str(resistencia)+'_'+str(temp)+'C_'+str(frec_ini)+'hz_sin_corregir_offset_ajuste.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)





#%% Recovery time

carpeta_salida = 'CurvaDiodo'
subcarpeta_salida = 'RecoveryTime'
subsubcarpeta_salida = 'UF4007'

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))   

if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))  

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
dato = 'int16'    
ind_nivel = 9
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
    
frec_ini = 1020
frec_fin = 1020
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

#%%
carpeta_salida = 'CurvaDiodo'
subcarpeta_salida = 'RecoveryTime'
subsubcarpeta_salida = 'UF4007'



data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

# Calibracion de los canales
data_in[:,:,0] = (data_in[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in[:,:,1] = (data_in[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])

tiempo = np.linspace(0,data_in.shape[1]-1,data_in.shape[1])/fs

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])     
#ax1 = ax.twinx()
ax.plot(tiempo,data_in[0,:,0],'-',label='',alpha=0.8)
ax.plot(tiempo,data_in[0,:,1],'-',color='red',label='',alpha=0.8)
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [s]')
ax.set_ylabel(u'Tensión [V]')

#%%


calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))

carpeta_salida = 'CurvaDiodo'
subcarpeta_salida = 'RecoveryTime'
subsubcarpeta_salida = '1N4007'

data_out_0 = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in_0 = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

# Calibracion de los canales
data_in_0[:,:,0] = (data_in_0[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in_0[:,:,1] = (data_in_0[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])+0.34-0.0033

subsubcarpeta_salida = '1N4148'

data_out_1 = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in_1 = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

# Calibracion de los canales
data_in_1[:,:,0] = (data_in_1[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in_1[:,:,1] = (data_in_1[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])+0.34-0.0070

tiempo_0 = np.linspace(0,data_in_0.shape[1]-1,data_in_0.shape[1])/fs
tiempo_1 = np.linspace(0,data_in_1.shape[1]-1,data_in_1.shape[1])/fs

subsubcarpeta_salida = 'UF4007'

data_out_2 = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out.npy'))
data_in_2 = np.load(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in.npy'))

# Calibracion de los canales
data_in_2[:,:,0] = (data_in_2[:,:,0]-calibracion_CH0_seno[1])/(calibracion_CH0_seno[0])
data_in_2[:,:,1] = (data_in_2[:,:,1]-calibracion_CH1_seno[1])/(calibracion_CH1_seno[0])+0.34-0.0070+0.0105

tiempo_0 = np.linspace(0,data_in_0.shape[1]-1,data_in_0.shape[1])/fs
tiempo_1 = np.linspace(0,data_in_1.shape[1]-1,data_in_1.shape[1])/fs
tiempo_2 = np.linspace(0,data_in_2.shape[1]-1,data_in_2.shape[1])/fs


fig = plt.figure(dpi=250)
ax = fig.add_axes([.12, .15, .35, .8])
#ax1 = ax.twinx()
ax.plot(tiempo_0,data_in_0[0,:,1],'-',label='Caida en resistencia - 1N4007',alpha=0.8)
ax.plot(tiempo_2,data_in_2[0,:,1],'-',label='Caida en resistencia - UF4007',alpha=0.8)
ax.plot(tiempo_1,data_in_1[0,:,1],'-',label='Caida en resistencia - 1N4148',alpha=0.8)

ax.set_title(u'Caida de tensión en resistencia en diodos 1N4007, UF4007 y 1N4148 utilizando un seno de '+str(frec_ini)+' Hz. Con corrección de offset.')
ax.legend()
ax.grid(linestyle='--')
ax.set_xlabel(u'Tiempo [s]')
ax.set_ylabel(u'Tensión [V]')
ax.set_xlim([0.615,0.620])

ax1 = fig.add_axes([.60, .15, .35, .8])
#ax1 = ax.twinx()
ax1.plot(tiempo_0,data_in_0[0,:,1],'-',label='Caida en resistencia - 1N4007',alpha=0.8)
ax1.plot(tiempo_2,data_in_2[0,:,1],'-',label='Caida en resistencia - UF4007',alpha=0.8)
ax1.plot(tiempo_1,data_in_1[0,:,1],'-',label='Caida en resistencia - 1N4148',alpha=0.8)

ax1.set_title(u'Detalle')
ax1.legend()
ax1.grid(linestyle='--')
ax1.set_xlabel(u'Tiempo [s]')
ax1.set_ylabel(u'Tensión [V]')
ax1.set_xlim([0.6171,0.6177])
ax1.set_ylim([-0.02,0.02])

figname = os.path.join(carpeta_salida,subcarpeta_salida, 'recovery_time.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)


#%% Temperatura

diodo = '1N4148'
carpeta_salida = 'CurvaDiodo'
subcarpeta_salida = 'Temperatura'
subsubcarpeta_salida = diodo
temp = 37

if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     

if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida))       

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
dato = 'int16'    
ind_nivel = 9
mic_level = 70
fs = 44100*8  
duracion = 5
muestras = int(fs*duracion) + int(fs*1)
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
        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
#        output_signal = signalgen_corrected('square',fr,amp,duration,fs,frec_send,fft_norm,[2,20500])
#        output_signal = np.append(output_signal,np.zeros(int(fs*1)))
        data_out[i,:,j] = output_signal
        
        


# Realiza medicion
offset_correlacion = 0#int(fs*(1))
steps_correlacion = 0#int(fs*(1))
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_out'+str(temp)),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida,subsubcarpeta_salida, 'data_in'+str(temp)),data_in)
