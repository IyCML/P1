# -*- coding: utf-8 -*-

"""
Estudio de linealidad. Análisis de señales adquiridas. Resultados

"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
from scipy import signal
import numpy.fft as fft

folder = '.\linealidad'
data_gen = '\data_out.npy'
data_rec = '\data_in.npy'

gen = np.load(folder+data_gen)
rec = np.load(folder+data_rec)

fs = 44100*8
# grafica dejando afuera los primeros 100 ms
#(donde la señal tiene oscilaciones)
#ajuste lineal
ti = int(fs*0.1)
tf = -int(fs*0.1)
x = gen[0,ti:tf,0]
y = rec[0,ti:tf,0]

def calibrate(x,y,type,chrec):
    """
    chgen = 0 for sine, 1 for Ramp
    chrec = 0, 1
    """
    if type =='sine':
        chgen = 0
    elif type == 'ramp':
        chgen = 1
    else:
        print('wrong type')

    z = np.polyfit(x,y,1)
    p = np.poly1d(z)
    rec_cor = (y-z[1])/z[0]
    fig1 = plt.figure()
    plt.plot(gen[chgen,ti:tf,chrec],rec[chgen,ti:tf,chrec],'.',label='%s CH %.f'%(type,chrec),markersize=1)
    plt.plot(x,p(x),'--', label = 'ajuste lineal')
    plt.xlabel('señal enviada [V]')
    plt.ylabel('señal recibida [u.a.]')
    plt.legend(loc='best')
    plt.grid(linestyle='--')
    fig2 = plt.figure()
    plt.title('señal calibrada')
    plt.plot(gen[0,ti:tf,0],rec_cor,'.',label='%s CH %.f'%(type,chrec),markersize=1)
    plt.xlabel('señal enviada [V]')
    plt.ylabel('señal recibida [V]')
    plt.legend(loc='best')
    plt.grid(linestyle='--')
    fig1.savefig('%s_CH%.f'%(type,chrec), dpi=300)
    fig2.savefig(folder+'%s_CH%.f_calibrada'%(type,chrec), dpi=300)

    return z, fig1, fig2

z0, fig1sen0,fig2sen0 = calibrate(x,y,'sine',0)
# figname = os.path.join(carpeta_salida, 'calibracion.png')
# fig.savefig(figname, dpi=300)
# plt.close(fig)
plt.show()
