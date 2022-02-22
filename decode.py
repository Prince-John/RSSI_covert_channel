from operator import delitem
import numpy as np
import time
from matplotlib import pyplot as plt
import threading
from progress.spinner import Spinner


def movingAvg(arr, position, numvals=50, wrap=0):
    # default to 3 pt moving average with wrap around on getting values 
    # arr       - array
    # posistion - start from this point on averages
    # numvals   - Number of values in moving average, default of 3
    # wrap      - wrap around to top or bottom of array if 1 (default), no if 0
    sumvals    = 0
    count      = 0    
    array_size = len(arr)
    # if less than numvals data, then just use what is available
    for i in range(numvals):
        # add an item to the list
        if (position - i >= 0 and position - 1 < array_size):
            sumvals = sumvals + arr[(position - i)]
            count   = count + 1
        # wrap backwards, goes to top of array, works in python
        elif (position - i < 0 and wrap == 1): 
            sumvals = sumvals + arr[(position - i)]
            count   = count + 1
        # wrap around to bottom of array with mod
        elif (position - i > array_size and wrap == 1):
            sumvals = sumvals + arr[(position - i)%array_size]
            count   = count + 1
    return sumvals/count


def read_level():
    f = open(r'/proc/net/wireless')
    data = f.read().splitlines()
    level = data[2].split()[3]
    f.close()
    return float(level)

def poll(tim = 1, rate =500):
    """Rate is the sampling rate, default set to 500 Hz; Time is sampling time in seconds, default 10 sec"""
    length = rate*tim
    data_in = np.zeros(length, dtype = float) 
    
    
    
    i = 0
    s1_time =np.zeros(1000000000, dtype = float) 
    ctr = 0
    
    start_time = time.time()
    current_time = start_time
    while((current_time-start_time) < tim):
        #s_time = time.time()
        if (current_time-start_time) > (1/rate)*(i+1):
            #print(f'current time: {(1/rate)*(i+1)}')
            data_in[i] = read_level()
            i+=1
            
        current_time = time.time()
        #print(f'loop time = {(time.time()-s_time)}')
        ctr+=1

    #print(f's = {s_time}')
    #sum = 0
    #for i in range(1000):
      #  sum += s1_time[i]
    #print(sum/1000)
    return data_in


def my_movAvg(data):
    data_out = [0]*len(data)
    for i in range(0,len(data)):
        data_out[i] = movingAvg(data, i)
    return data_out




def waiting():
    
    bar = Spinner('Aquring data: ')
       
    while(True):
        time.sleep(0.2)
        bar.next()
        global stop_threads
        if stop_threads:
            bar.finish()
            break


stop_threads = False
t1 = threading.Thread(target = waiting)
t1.start()
data = poll(120,150)
stop_threads = True
t1.join()


print(data.shape)
print("Moving Avg")
avg_data = my_movAvg(data)


f = open(r'data1.txt', 'w')
time = [0]*len(data)
for i in range(len(data)):
    time[i]=i
    f.write(f'{i}\t{avg_data[i]}\t\n')
f.close()
#print(time)

#print(avg_data)



fig = plt.figure()
plt.plot(time, data)
plt.plot(time, avg_data)
plt.show()

f = open(r'data.txt', 'w')
