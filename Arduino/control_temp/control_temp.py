# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 09:17:11 2018

@author: Marco
"""

import win32pipe, win32file,time,struct
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from multiprocessing import Process
from timeit import default_timer as timer
import sys
import datetime 
import serial
import os

tec_onoff = 0
tec_onoff_s = 0
temp_setpoint = 12
delta_temp = 2
mediciones_por_archivo = 2000
cont = 0
iter_cont = 5
start = datetime.datetime.now()

arduino = serial.Serial('COM5', 9600, timeout=0.3)


tt = 0
ind_med = 0
ind_arch = 0
guardar_onoff = 0
file_mon = 0
#temp_setpoint = 15


guardar_onoff = 0
filename_path = 'hola.dat'

if guardar_onoff == 1:
    j = 0
    while 1:
        filename_path_mon = os.path.join(filename_path, 'MONITOREO_' + '%02d' % (j))
        if not os.path.isdir(filename_path_mon):
            break
        j = j + 1
            
     #filename_path_mon = os.path.join(filename_path, 'MONITOREO')
    os.mkdir(filename_path_mon)    
    ind_arch = 0
    inttostr = '%06d' % (ind_arch)
    file_mon = open(os.path.join(filename_path_mon,inttostr + '.val' ),'w')    
    file_mon.write('hora, tec_onoff, temp_act[C], temp_set[C], temp_set_1[C] \n')




delta_t_sec = 120.
step = 0
ultimo_paso = 0
delta_actual = delta_t_sec+1
temp_setpoint_rec = 0

time.sleep(5)

while step < 15:
    
    
    while arduino.inWaiting() > 500:
        arduino.readline()
    
    if delta_actual > delta_t_sec:
        ultimo_paso = datetime.datetime.now()
        step = step + 1            
        temp_setpoint = temp_setpoint + delta_temp
        print('Paso: ' + str(step))

    if temp_setpoint_rec != temp_setpoint:
        arduino.write(struct.pack('<bif',0,int(tec_onoff),temp_setpoint))  
        arduino.flush()
         
    tiempo_actual = datetime.datetime.now()
    delta_actual = np.abs((tiempo_actual-ultimo_paso).total_seconds())
    
    while arduino.inWaiting():
#        a = arduino.read(1)
#        b = arduino.read(1)
        #print (a,b)
    
        #print (arduino.readline())
        rawString = arduino.readline()
        array_serial = np.fromstring(rawString, dtype=float, count=-1, sep=',')    
        
        if len(array_serial) == 13:  
            
            temp_actual = array_serial[1]
            temp_setpoint1 = array_serial[3]
            temp_setpoint_rec = array_serial[12]
                
            cont = cont + 1                

            if guardar_onoff == 1:
                ind_med = ind_med + 1                    
                ind_med = ind_med%mediciones_por_archivo + 1
                    
                if ind_med == mediciones_por_archivo:
                    file_mon.close()
                    
                    ind_arch = ind_arch + 1
                    inttostr = '%06d' % (ind_arch)                        
                    file_mon = open(os.path.join(filename_path_mon,inttostr + '.val' ),'w') 
                    file_mon.write('hora, tec_onoff, temp_act[C], temp_set[C], temp_set_1[C] \n')

                if tec_onoff == 0:
                    tec_onoff_s = 1
                else:
                    tec_onoff_s = 0
                                             
                        
                tiempo_actual = datetime.datetime.now()
                data_string2 = str(tiempo_actual)+ ', ' + str(tec_onoff_s) +  ', ' + str(temp_actual) + ', ' + str(temp_setpoint)  + ', ' + str(temp_setpoint1) + '\n'   
                    
                #print data_string2   
                    
                if hasattr(file_mon, 'closed'):
                    if not file_mon.closed:                              
                        file_mon.write(data_string2)
                
                
                
            
    #print ' '
    
              
        
                            





