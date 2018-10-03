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
from P1_funciones import par2ind


params = {'legend.fontsize': 14,
          'figure.figsize': (14, 9),
         'axes.labelsize': 24,
         'axes.titlesize':18,
         'font.size':18,
         'xtick.labelsize':24,
         'ytick.labelsize':24}
pylab.rcParams.update(params)




    
#%%

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
    
#dato = 'int16' 
#fs = 44100*8  
#duracion = 30
#muestras = int(fs*duracion)
#input_channels = 2
#output_channels = 2
#amplitud = 1 #V
#frec_ini = 500
#frec_fin = 500
#pasos_frec = 1
#delta_frec = (frec_fin-frec_ini)/(pasos_frec+1)
#data_out = np.zeros([pasos_frec,muestras,output_channels])
#
#for i in range(pasos_frec):
#    parametros_signal = {}
#    fs = fs
#    amp = amplitud
#    fr = frec_ini + i*delta_frec
#    duration = duracion
#    
#    
#    output_signal = signalgen('sine',fr,amp,duration,fs)
#    data_out[i,:,0] = output_signal
#    data_out[i,:,1] = output_signal
#        
#        
## Realiza medicion
#offset_correlacion = 0#int(fs*(1))
#steps_correlacion = 0#int(fs*(1))
#data_in, retardos = play_rec(fs,input_channels,data_out,'no',offset_correlacion,steps_correlacion,dato=dato)
#
#
#fig = plt.figure(figsize=(14, 7), dpi=250)
#ax = fig.add_axes([.12, .15, .75, .8])
#ax1 = ax.twinx()
#ax.plot(data_in[0,:,0] ,alpha=0.8)
#ax1.plot(data_in[0,:,1] ,color='red',alpha=0.8)


#%%
# CALIBRACION PARLANTE PLACA MARCO PC CASA

carpeta_salida = 'Calibracion'
subcarpeta_salida = 'Parlante'
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     

parlante_levels = np.array([10,20,30,40,50,60,70,80,90,100])
tension_rms_v_ch0 = np.array([0.050, 0.142, 0.284, 0.441, 0.678, 0.884, 1.143, 1.484, 1.771, 2.280])
amplitud_v_ch0 = tension_rms_v_ch0*np.sqrt(2)
tension_rms_v_ch1 = np.array([0.050, 0.146, 0.291, 0.451, 0.693, 0.904, 1.170, 1.518, 1.812, 2.330])
amplitud_v_ch1 = tension_rms_v_ch1*np.sqrt(2)

np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'wp_amp_ch0'),amplitud_v_ch0)
np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'wp_amp_ch1'),amplitud_v_ch1)
np.save(os.path.join(carpeta_salida,subcarpeta_salida, 'parlante_levels'),parlante_levels)


#%%
carpeta_salida = 'Calibracion'
subcarpeta_salida = 'Parlante'
# Calibracion parlante
amplitud_v_ch0 = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'wp_amp_ch0.npy'))
amplitud_v_ch1 = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'wp_amp_ch1.npy'))
parlante_levels = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'parlante_levels.npy'))
mic_levels = [10,20,30,40,50,60,70,80,90,100]

#%%
dato = 'int16' 

carpeta_salida = 'Calibracion'
subcarpeta_salida = dato
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     

# Genero matriz de señales: ejemplo de barrido en frecuencias en el canal 0
    
    
    
par_level = 30
mic_level = 100
fs = 44100*8  
duracion = 0.5
muestras = int(fs*duracion)
input_channels = 2
output_channels = 2
amplitud = 1
frec_ini = 500
frec_fin = 500
pasos = 2
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
        data_out[i,:,0] = output_signal
        
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
data_in, retardos = play_rec(fs,input_channels,data_out,'si',offset_correlacion,steps_correlacion,dato=dato)

np.save(os.path.join(carpeta_salida,subcarpeta_salida, dato+'_wm'+str(mic_level)+'_data_out'),data_out)
np.save(os.path.join(carpeta_salida,subcarpeta_salida, dato+'_wm'+str(mic_level)+'_data_in'),data_in)



#%%

# CAlibracion para nivel de parlante 70, y nivel de microfono de 80
# En este valor de nivel de parlante Amplitud = 1 ==> 1V de amplitud
# En este nivel de parlante la señal de amplitud 1 (1V) ocupa todo el rango de medición
# Esto vale para la placa de pc de escritorio de casa de Marco y windows 10

dato = 'int16' 
par_level = 30
ind_nivel = par2ind(par_level,parlante_levels)

carpeta_salida = 'Calibracion'
subcarpeta_salida = dato
if not os.path.exists(carpeta_salida):
    os.mkdir(carpeta_salida)
    
if not os.path.exists(os.path.join(carpeta_salida,subcarpeta_salida)):
    os.mkdir(os.path.join(carpeta_salida,subcarpeta_salida))     

for mic_level in mic_levels:


    data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, dato + '_wm'+str(mic_level)+'_data_out.npy'))
    data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, dato +  '_wm'+str(mic_level)+'_data_in.npy'))
    amplitud_v_chs = [amplitud_v_ch0[ind_nivel],amplitud_v_ch1[ind_nivel]] #V
    
    formas = ['Seno','Rampa']
    canales = ['CH0','CH1']
    
    for i in range(2):
        
        for j in range(2): #por canal
            
            amplitud_v = amplitud_v_chs[j]
                
            ajuste = np.polyfit(data_out[i,int(fs*0.1):-int(fs*0.1),j]/amplitud*amplitud_v,data_in[i,int(fs*0.1):-int(fs*0.1),j],1)
            
            
            fig = plt.figure(dpi=250)
            ax = fig.add_axes([.15, .15, .75, .8])        
            ax.plot(data_out[i,int(fs*0.1):-int(fs*0.1),j]/amplitud*amplitud_v,data_in[i,int(fs*0.1):-int(fs*0.1),j],'--',color='blue',alpha=0.8,label='Señal')
            ax.plot(data_out[i,int(fs*0.1):-int(fs*0.1),j]/amplitud*amplitud_v,data_out[i,int(fs*0.1):-int(fs*0.1),j]/amplitud*amplitud_v*ajuste[0]+ajuste[1],'--',color='red',alpha=0.8,label='Ajuste')
            ax.grid(linestyle='--')
            ax.legend(loc=4)
            ax.text(0.1,0.8,'Ajuste: ax + b', transform=ax.transAxes)
            ax.text(0.1,0.75,'a: ' '{:6.2e}'.format(ajuste[0]) + ' [cuentas/V]', transform=ax.transAxes)
            ax.text(0.1,0.70,'b: ' '{:6.2e}'.format(ajuste[1]) + ' [cuentas]', transform=ax.transAxes)
            ax.set_xlabel('Señal enviada [V]')
            ax.set_ylabel('Señal recibida [cuentas]')
            #ax.set_title(u'Señal enviada y adquirida en ' + canales[j] + ' utilizando función ' + formas[i] + '. Nivel de parlante en '+ str(windows_nivel[ind_nivel]) +'/100 y microfono '+str(mic_level)+'/100' )
            figname = os.path.join(carpeta_salida,subcarpeta_salida, 'ajuste_'+canales[j]+ '_'+formas[i]+  '_wm'+str(mic_level)+'_'+dato+'.png')
            fig.savefig(figname, dpi=300)  
            plt.close(fig)
    
            
            
            fig = plt.figure(dpi=250)
            ax = fig.add_axes([.15, .15, .75, .8])        
            ax.plot(data_out[i,int(fs*0.1):-int(fs*0.1),j]/amplitud*amplitud_v,(data_in[i,int(fs*0.1):-int(fs*0.1),j]-ajuste[1])/ajuste[0],'--',color='red')       
            ax.set_xlabel('Señal enviada [V]')
            ax.set_ylabel('Señal recibida [V]')   
            ax.grid(linestyle='--')
            #ax.set_title(u'Señal enviada y adquirida en ' + canales[j] + ' utilizando función ' + formas[i] + '. Nivel de parlante en '+ str(windows_nivel[ind_nivel]) +'/100 y microfono '+str(mic_level)+'/100' )
            figname = os.path.join(carpeta_salida,subcarpeta_salida, 'conversion_'+canales[j]+ '_'+formas[i]+  '_wm'+str(mic_level)+'_'+dato+'.png')
            fig.savefig(figname, dpi=300)  
            plt.close(fig)        
    
    
            np.save(os.path.join(carpeta_salida,subcarpeta_salida,formas[i] + '_' + canales[j] + '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'),ajuste)
        
        
#%%

carpeta_salida = 'Calibracion'
subcarpeta_salida = dato

par_level = 30
ind_nivel = par2ind(par_level,parlante_levels)

rango_ch0 = np.array([])
rango_ch1 = np.array([])

for i,mic_level in enumerate(mic_levels):
    
    calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
    calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))   
    
    rango_ch0 = np.append(rango_ch0,2**15/calibracion_CH0_seno[0])
    rango_ch1 = np.append(rango_ch1,2**15/calibracion_CH1_seno[0])
    

mic_levels_array = np.asarray(mic_levels)

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])  
ax.semilogy(mic_levels_array,rango_ch0,'o',label='CH0',alpha=0.7,markersize=10)
ax.semilogy(mic_levels_array,rango_ch1,'o',label='CH1',alpha=0.7,markersize=10)
ax.axhline(2.05,linestyle='--',color='black',alpha=0.8,label='Limitación de la entrada')    
ax.grid(linestyle='--')    
ax.legend()
ax.set_ylim([0.1,100])
ax.set_xlabel('Nivel de micrófono')
ax.set_ylabel(u'Rango positivo receptor [V]')   
#ax.set_title(u'Rango del receptor en función del nivel del micrófono.')   
figname = os.path.join(carpeta_salida, 'respuesta_por_nivel_microfono_rango.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)    
        

#%% Medimos linealidad en amplitud
#Linealidad para seno

#data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_out.npy'))
#data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, 'data_in.npy'))
#
#
#lin_sen_ch0 = data_in[0,:,0]/data_out[0,:,0]
#lin_sen_ch1 = data_in[0,:,1]/data_out[0,:,1]
#lin_ramp_ch0 = data_in[1,:,0]/data_out[1,:,0]
#lin_ramp_ch1 = data_in[1,:,1]/data_out[1,:,1]
#
#fig = plt.figure(figsize=(14, 7), dpi=250)
#ax = fig.add_axes([.12, .15, .75, .8])
#ax.plot(data_out[0,int(fs*0.1):-int(fs*0.1),0],data_in[0,int(fs*0.1):-int(fs*0.1),0],'.',label='Seno en CH0',markersize=1)
#ax.plot(data_out[0,int(fs*0.1):-int(fs*0.1),1],data_in[0,int(fs*0.1):-int(fs*0.1),1],'.',label='Seno en CH1',markersize=1)
#ax.plot(data_out[1,int(fs*0.1):-int(fs*0.1),0],data_in[1,int(fs*0.1):-int(fs*0.1),0],'.',label='Rampa en CH0',markersize=1)
#ax.plot(data_out[1,int(fs*0.1):-int(fs*0.1),1],data_in[1,int(fs*0.1):-int(fs*0.1),1],'.',label='Rampa en CH1',markersize=1)
#ax.set_xlabel('señal enviada')
#ax.set_ylabel('señal recibida [u.a.]')
#ax.legend(loc=2)
#ax.grid(linestyle='--')
#figname = os.path.join(carpeta_salida,subcarpeta_salida, 'calibracion.png')
#fig.savefig(figname, dpi=300)  
#plt.close(fig)

#%%
       
carpeta_salida = 'Calibracion'
subcarpeta_salida = dato 

mic_level = 100          
par_level = 30
ind_nivel = par2ind(par_level,parlante_levels)   
 
amplitud = 1
amplitud_v_chs = [amplitud_v_ch0[ind_nivel],amplitud_v_ch1[ind_nivel]] #V  

fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])   

for i,mic_level in enumerate(mic_levels):
    
    data_out = np.load(os.path.join(carpeta_salida,subcarpeta_salida, dato+  '_wm'+str(mic_level)+'_data_out.npy'))
    data_in = np.load(os.path.join(carpeta_salida,subcarpeta_salida, dato +  '_wm'+str(mic_level)+'_data_in.npy'))
  
    amplitud_v = amplitud_v_chs[0]
    ax.plot(data_out[0,int(fs*0.1):-int(fs*0.1),0]/amplitud*amplitud_v,data_in[0,int(fs*0.1):-int(fs*0.1),0],'--',color=cmap(float(i)/len(mic_levels)),label='Nivel de mic:'+str(mic_level),alpha=0.7)
    
ax.axhline(2**15,linestyle='--',color='black',alpha=0.8)    
ax.axhline(-2**15,linestyle='--',color='black',alpha=0.8)    
ax.set_xlabel('Señal enviada [V]')
ax.set_ylabel('Señal recibida [cuentas]')    
#ax.set_title(u'Señal recibida al variar el nivel de micrófono')   
ax.grid(linestyle='--')    
ax.legend()
#ax.legend(bbox_to_anchor=(1.05, 1.00))
figname = os.path.join(carpeta_salida, 'respuesta_por_nivel_mic.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)         


#%%

carpeta_salida = 'Calibracion'
subcarpeta_salida = dato


fig = plt.figure(dpi=250)
ax = fig.add_axes([.15, .15, .75, .8])  
ax.plot(parlante_levels,amplitud_v_ch0,'o',label='CH0',alpha=0.7,markersize=10)
ax.plot(parlante_levels,amplitud_v_ch1,'o',label='CH1',alpha=0.7,markersize=10)
ax.grid(linestyle='--')    
ax.legend()
ax.set_xlabel('Nivel de parlante')
ax.set_ylabel(u'Amplitud señal enviada [V]')   
#ax.set_title(u'Amplitud de señal enviada en función de nivel de parlante. Amplitud de salida = 1')   
figname = os.path.join(carpeta_salida, 'respuesta_por_nivel_parlante.png')
fig.savefig(figname, dpi=300)  
plt.close(fig)


#%%

dato = 'int16' 
carpeta_salida = 'Calibracion'
subcarpeta_salida = dato
mic_level = 100      


for i,mic_level in enumerate(mic_levels):
    
    calibracion_CH0_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH0'+  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
    calibracion_CH1_seno = np.load(os.path.join('Calibracion',dato, 'Seno_CH1' +  '_wm'+str(mic_level)+'_'+dato+'_ajuste.npy'))
    
    print(1/calibracion_CH0_seno[0]*1000000)
    #print(2**15/calibracion_CH0_seno[0])
     