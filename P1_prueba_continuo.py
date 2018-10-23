# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 13:39:59 2018

@author: Marco
"""

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

from P1_funciones import play_rec_continuo

#%%
fs = 44100
frames_per_buffer = 4*256
chunks_buffer = 1000


callback_variables = []

def callback(callback_variables,*args):
    
    input_buffer = args[0]
    output_buffer = args[1]
    i = args[2]
    frames_per_buffer = args[3]
    chunks_buffer = args[4]
    fs = args[5]
    
    output_buffer_i = 0.1*np.sin(2.*np.pi*np.arange(i*frames_per_buffer,(i+1)*frames_per_buffer)*1000/fs)
    
    return output_buffer_i

input_buffer, output_buffer = play_rec_continuo(fs,frames_per_buffer,chunks_buffer,callback,callback_variables)

dfgd

#%%
todo = np.reshape(input_buffer,input_buffer.shape[0]*input_buffer.shape[1])
senal =  0.1*np.sin(2.*np.pi*np.arange(256*2*1000)*(1000)/fs)

todo = todo/todo.max()
senal = senal/senal.max()

plt.plot(todo,alpha=0.5)
plt.plot(senal,alpha=0.5)


plt.plot(todo-senal)


#for i in range(input_buffer.shape[0]):
#    plt.axvline(i*input_buffer.shape[1],linestyle='--',color='red')


#%%

output_channels = 1

p = pyaudio.PyAudio()

stream_output = p.open(format=pyaudio.paFloat32,
                channels = output_channels,
                rate = fs,
                output = True,                  
    ) 

todo_out = todo/todo.max()
todo_out = todo_out.astype(np.float32)

stream_output.start_stream()
stream_output.write(todo_out)
stream_output.stop_stream()    

stream_output.close()
p.terminate() 

#%%
plt.plot(todo_out)