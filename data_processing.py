from email.mime import base
from tkinter.tix import Tree
import numpy as np
from matplotlib import pyplot as plt

debug = True


with open(r'data1.txt', 'r') as f:
    lines = f.readlines()

    data = [0]*len(lines)
    time = [0]*len(lines)
    i =0
    for line in lines:
        data[i] = float(line.split('\t')[1])
        time[i] = i
        i+=1
    
    



def edge(arr, loc,  thresh, detect_width = 100, debug =False):
    #detect_width is dependent on the bitrate of the transmission, future versions should include a lookup table and itterations to optimize for the start sequence correct detection accuracy.    
    if loc < detect_width:
        loc =detect_width
    elif loc >=(len(arr)-detect_width):
        loc = loc-detect_width
    s1 = sum(arr[loc-detect_width:loc])/detect_width
    s2 = sum(arr[loc:loc+detect_width])/detect_width
    
    if debug: print(f's1: {s1}, s2: {s2}, loc: {loc}')
    if abs(s1-s2)>thresh:
        return True
    return False





a = 0
count = 0
edge_count = 0
bit_stream =[]
edge_loc = [0]*len(data)
thresh = -63





def find_pulses(data):
    edge_loc = [0]*len(data)
    for i in range(len(data)):
        
        if edge(data, i,3, detect_width= 50):
            edge_loc[i] = 1
    return edge_loc



def locate_sync(data, debug = False):
    """ Sudo state machine,
    
    s0 = looking for first bit
    s1 = counting bits until 10
    s2 = baseline reading start
        
    Avg bit length is calculated by counting samples between falling edges in the intro sequence. 
    """

    falling_edge_pos = 0
    bit_state = 0
    bit_length = [] 
    bit_count = 0
    baseline_level = 0

    for i in range(len(data)):
        if bit_state <= 1:

            if data[i] == 1 and (data[i+1] == 1 or data[i+2] == 1):
                bit_state = 1
            elif data[i] == 1 and (data[i+1] == 0 and data[i+2] == 0 and data[i+2] == 0):
                                
                if falling_edge_pos != 0: bit_length.append(i-falling_edge_pos)
                
                falling_edge_pos=i

                bit_count += 1
                if bit_count == 10: 
                    bit_state = 2
                    avg_bit_len = sum(bit_length)/len(bit_length)
                count_since_edge = 0
                if debug: print(f'Bitstream, current bitlengths : {bit_length}; Current position: {i}')       
        if bit_state == 2:
            baseline_level = i
            break

    if debug: print(f'Avg bit length: {avg_bit_len} ')

    return round(avg_bit_len), baseline_level


def baseline_reading(bit_len, baseline_start, edge_data, data, debug = False):

    reading_len = round(bit_len*5)
    baseline_high_start = baseline_start+round(reading_len)
    baseline_high_end = baseline_high_start+round(reading_len)
    baseline_end = baseline_high_end+round(reading_len)

    baseline_low_level = (sum(data[baseline_start:baseline_high_start])+sum(data[baseline_high_end:baseline_end]) )/(reading_len*2)
    baseline_high_level = (sum(data[baseline_high_start:baseline_high_end]))/reading_len
    
    thresh = (baseline_low_level + baseline_high_level)/2

    if debug: print(f'The baseline low is : {baseline_low_level}, The baseline high is :{baseline_high_level}\n s0 = {baseline_start}, s1 = {baseline_high_start},s2 = {baseline_high_end},s3 = {baseline_end}')
    
    return thresh 




def discretize_stream(pulses, data, thresh, debug = False):


    count = 0
    last_edge = 0
    bit_stream = []
    for i in range(len(pulses)):
        
        if pulses[i] == 1:
            avg_signal_level = sum(data[last_edge:i])/count
            if debug: print(f'Avg sig level {avg_signal_level}, p_i = {count}')
            if avg_signal_level>=thresh:
                bit_stream.extend([1]*count)
                if debug: print(f'Sum between edges: {avg_signal_level}')
            else:
                bit_stream.extend([0]*count)

            count = 0
            last_edge = i
        count += 1

    return bit_stream

    


def generate_bitstream(dis_stream, bit_length, baseline_start, debug = False):

    """Generates the final stream of decoded bits from a discreete input stream. It verifies the transmission start with baseline start refrence and edge detection"""

    read_start = baseline_start+bit_length*15

    bit_stream = []

    while dis_stream[read_start] == 0:  read_start +=1

    for i in range(read_start, len(dis_stream), bit_length):

        bit_stream.append(round(sum(dis_stream[i:i+bit_length])/bit_length))
  
    if debug: print(f'read start at : {read_start}')

    return bit_stream




def decrypt(message):
    MORSE_CODE_DICT = { 'A':'10111', 'B':'111010101',
                    'C':'11101011101', 'D':'1110101', 'E':'1',
                    'F':'101011101', 'G':'111011101', 'H':'1010101',
                    'I':'101', 'J':'1011101110111', 'K':'111010111',
                    'L':'101110101', 'M':'1110111', 'N':'11101',
                    'O':'11101110111', 'P':'10111011101', 'Q':'1110111010111',
                    'R':'1011101', 'S':'10101', 'T':'111',
                    'U':'1010111', 'V':'101010111', 'W':'101110111',
                    'X':'11101010111', 'Y':'1110101110111', 'Z':'11101110101',
                    '1':'10111011101110111', '2':'101011101110111', '3':'1010101110111',
                    '4':'10101010111', '5':'101010101', '6':'11101010101',
                    '7':'1110111010101', '8':'111011101110101', '9':'11101110111011101',
                    '0':'1110111011101110111', ',':'1110111010101110111', '.':'10111010111010111',
                    '?':'101011101110101', '/':'1110101011101', '-':'111010101010111',
                    '(':'111010111011101', ')':'1110101110111010111'}
    message = ''.join(str(i) for i in message)
    # extra space added at the end to access the
    # last morse code
    message += '                   '
    i = 0
    decipher = ''
    citext = ''
    for letter in message:
 
        # checks for space
        if (letter != '0'):
            if i == 1 :
                citext += '0'
 
            # storing morse code of a single character
            citext += letter
            # counter to keep track of space
            i = 0
 
        # in case of space
        else:
            # if i = 1 that indicates a new character
            i += 1
            # if i = 2 that indicates a new word
            if i == 3 :
                # accessing the keys using their values (reverse of encryption)
                decipher += list(MORSE_CODE_DICT.keys())[list(MORSE_CODE_DICT
                .values()).index(citext)]
                citext = ''
                 
            elif i == 7 :
                # adding space to separate words
                decipher += ' '
                
 
    return decipher








debug = False   


pulses = find_pulses(data)
bit_len, baseline_start = locate_sync(pulses, debug= debug)
thresh = baseline_reading(bit_len, baseline_start, pulses, data, debug= debug)
discrete_stream = discretize_stream(pulses, data, thresh, debug= False)

bit_stream = generate_bitstream(discrete_stream, bit_len, baseline_start)
print(bit_stream)
print(decrypt(bit_stream))




    



fig = plt.figure()
plt.subplot(3,1,3)
plt.plot(discrete_stream)
plt.subplot(3,1,1)
plt.plot(time, data)
plt.subplot(3,1,2)
plt.stem(pulses, use_line_collection=True)
plt.show()



