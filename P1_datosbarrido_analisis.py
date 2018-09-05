# -*- coding: utf-8 -*-
# import pyaudio
import numpy as np
import matplotlib.pyplot as plt
# import threading
import numpy.fft as fft
# import datetime
# import time
# import matplotlib.pylab as pylab
from scipy import signal

# carga datos y analiza amplitudes de la señal
carpeta = 'C:\\Leslie\\Materias\\Instrumentación y control\\Clase 1_caracterizacioncomp\\P1\\respuesta_emisor_receptor\\respuesta_emisor_receptor\\'
send = 'data_send_rango_0.npy'
frec = 'frecs_send_rango_0.npy'
acq = 'data_acq_rango_0.npy'
data1_send = np.load(carpeta+send)
data1_acq = np.load(carpeta+acq)
data1_frec = np.load(carpeta+frec)
a1 = []
s1=[]
for i in range(len(data1_send)):
    fft1_send = abs(fft.fft(data1_send[i,:]))
    fft1_send = fft1_send[0:int(len(fft1_send)/2)]
    fft1_acq = abs(fft.fft(data1_acq[i,:]))
    fft1_acq = fft1_acq[0:int(len(fft1_acq)/2)]
    s1.append(np.max(fft1_send)/len(fft1_send)) #amplitud señal enviada
    a1.append(np.max(fft1_acq)/len(fft1_acq)) #amplitud señal recibida

send2 = 'data_send_rango_1.npy'
frec2 = 'frecs_send_rango_1.npy'
acq2 = 'data_acq_rango_1.npy'
data2_send = np.load(carpeta+send2)
data2_acq = np.load(carpeta+acq2)
data2_frec = np.load(carpeta+frec2)
a2 = []
s2=[]
for i in range(len(data2_send)):
    fft2_send = abs(fft.fft(data2_send[i,:]))
    fft2_send = fft2_send[0:int(len(fft2_send)/2)]
    fft2_acq = abs(fft.fft(data2_acq[i,:]))
    fft2_acq = fft2_acq[0:int(len(fft2_acq)/2)]
    s2.append(np.max(fft2_send)/len(fft2_send)) #amplitud señal enviada
    a2.append(np.max(fft2_acq)/len(fft2_acq)) #amplitud señal recibida
send3 = 'data_send_rango_3.npy'
frec3 = 'frecs_send_rango_3.npy'
acq3 = 'data_acq_rango_3.npy'
data3_send = np.load(carpeta+send3)
data3_acq = np.load(carpeta+acq3)
data3_frec = np.load(carpeta+frec3)
a3 = []
s3=[]
for i in range(len(data3_send)):
    fft2_send = abs(fft.fft(data3_send[i,:]))
    fft2_send = fft2_send[0:int(len(fft2_send)/2)]
    fft2_acq = abs(fft.fft(data3_acq[i,:]))
    fft2_acq = fft2_acq[0:int(len(fft2_acq)/2)]
    s3.append(np.max(fft2_send)/len(fft2_send)) #amplitud señal enviada
    a3.append(np.max(fft2_acq)/len(fft2_acq)) #amplitud señal recibida

plt.figure()#figsize=(14, 7), dpi=250)
plt.semilogx(data1_frec,a1,'.r',data1_frec,s1)
plt.semilogx(data2_frec,a2,'.r',data2_frec,s2)
plt.semilogx(data3_frec,a3,'.r',data3_frec,s3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Amplitud [u.a.]')
# plt.legend()
# plt.figure()
# plt.plot(fft1_acq)
# plt.plot(data1_acq[6,:])
plt.show()
