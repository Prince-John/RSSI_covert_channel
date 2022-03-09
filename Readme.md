# Covert Channel Lab 
### CSE569 Lab 1 Spring 2022

Using RSSI modulation to transmit data over a wifi network. 

How to: 

Both devices must be connected to the same wireless network for this to  work.

-To transmit data modify the ssh configuration in the `transmission.ipynb` notebook to match the settings for your router. 

-Start aquring  data using the `decode.py` script. By default it will collect data for 10 secs and write to a file in the same directory. These parameters can be adjusted using command line arguments. Run --help to see more. 

-Once the data has been acquired run the `data_processing.py` script to process the singal into the message output and plot the signal strength over time. If the program cannot decode the morse encoding. It will display an error message. The message can still be recovered by manual decoding of the descrete stream plot. 
