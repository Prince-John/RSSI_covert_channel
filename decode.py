from operator import delitem
import numpy as np
import time
from matplotlib import pyplot as plt
import threading
import argparse
from progress.spinner import Spinner


parser = argparse.ArgumentParser(description='Data for this program.')

parser.add_argument('--tim', action='store', type=int, default=10,
                    help='time for data aqusition in seconds')

parser.add_argument('--rate', action='store', type=int, default=150,
                    help='rate of sample collection in samples per sec, default is 150 Hz')
parser.add_argument('--dest', action='store', type=str, default='data.txt',
                    help='destination location for data to be written to file.')
parser.add_argument('--debug', action='store_true', 
                    help='specifies if debug statements are printed')
args = parser.parse_args()





def movingAvg(arr, position, numvals=50, wrap=0):
    # This function has been reused from sample code provided for ESE 205 course with permission from Dr.James Feher 

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

def poll(tim = 10, rate =500):
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
data = poll(args.tim,args.rate)

stop_threads = True
t1.join()



avg_data = my_movAvg(data)


f = open(args.dest, 'w')
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
