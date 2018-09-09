# -*- coding: utf-8 -*-

"""
Estudio de linealidad. Análisis de señales adquiridas. Resultados

"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
from scipy import signal
import numpy.fft as fft
import os
from decimal import Decimal


folder = '.\linealidad'
data_gen = '\data_out.npy'
data_rec = '\data_in.npy'

gen = np.load(folder+data_gen)
rec = np.load(folder+data_rec)

fs = 44100*8
# grafica dejando afuera los primeros 100 ms
#(donde la señal tiene oscilaciones)

def calibrate(gen,rec,type,chrec):
    """
    plot received vs sent signal, from ti to tf samples.
    chgen = 0 for sine, 1 for Ramp
    chrec = 0, 1
    """
    ti = int(fs*0.1)
    tf = -int(fs*0.1)

    if type =='sine':
        chgen = 0
    elif type == 'ramp':
        chgen = 1
    else:
        print('wrong type')

    x = gen[chgen,ti:tf,chrec]
    y = rec[chgen,ti:tf,chrec]

    z = np.polyfit(x,y,1)
    p = np.poly1d(z)
    rec_cor = (y-z[1])/z[0]
    # fig1 = plt.figure()
    # plt.plot(x,y,'.',label='%s CH %.f'%(type,chrec),markersize=1)
    # plt.plot(x,p(x),'--', label = 'ajuste lineal %.2E x + %.2E' %(z[0], z[1]))
    # plt.xlabel('señal enviada [V]')
    # plt.ylabel('señal recibida [u.a.]')
    # plt.legend(loc='best')
    # plt.grid(linestyle='--')
    # fig2 = plt.figure()
    # plt.title('señal calibrada %.2E x + %.2E' %(z[0], z[1]))
    # plt.plot(x,rec_cor,'.',label='%s CH %.f'%(type,chrec),markersize=1)
    # plt.xlabel('señal enviada [V]')
    # plt.ylabel('señal recibida [V]')
    # plt.legend(loc='best')
    # plt.grid(linestyle='--')
    #
    # figname1 = os.path.join(folder, '%s_CH%.f'%(type,chrec))
    # figname2 = os.path.join(folder,'%s_CH%.f_calibrada'%(type,chrec))
    # fig1.savefig(figname1, dpi=300)
    # fig2.savefig(figname2, dpi=300)

    return z#, fig1, fig2

z0s = calibrate(gen,rec,'sine', 0)#[0]
z1s = calibrate(gen,rec,'sine', 1)#[0]

#cargo datos del diodo
fdiodo = '.\curva_diodo'
data_diodo = '\data_in_ramp.npy'
datagen_diodo = '\data_out_ramp.npy'

gen_diodo = np.load(fdiodo+datagen_diodo)
rec_diodo = np.load(fdiodo+data_diodo)

caida_tot = (rec_diodo[0,:,0]-z0s[1])/z0s[0]
caida_res = (rec_diodo[0,:,1]-z1s[1])/z1s[0]
caida_diodo = caida_tot - caida_res
plt.figure()
plt.plot(caida_diodo,'r', label='diodo')
plt.plot(caida_res, label = 'resistencia')
plt.plot(caida_tot,'k', label = 'total')
plt.plot(gen_diodo[0,:,0],'g',label = 'generada')
# plt.xlabel()
plt.ylabel('caída de tensión [V]')
plt.legend()
plt.figure()
plt.plot(caida_res,caida_diodo)

plt.show()
