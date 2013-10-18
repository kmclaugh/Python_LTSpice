#!/usr/bin/python
# Python Code used for testing a photoresistor_array circuit in LTSpice by rewriting the netlist file with new
# parameters, running the netlist in LTSpice, and interpreting the output
import re
import os
from python_ltspice_tools import *

#process original file
net_filename = "/home/kevin/.wine/drive_c/Program Files/LTC/LTspiceIV/Photoresistor_Array/Photoresistor_Array.net"
parameter_header_name = "Resistance Parameters"
return_values = process_file(net_filename,parameter_header_name)
original_file_list = return_values[0]
parameter_lines = return_values[1]

#change parameters, create and run new file
change_params = [("R01","5k"),("R11","10k")]
current_file_list = switch_param_equals(change_params,original_file_list,parameter_lines)
new_net_filenames = write_new_net_file(current_file_list,original_filename=net_filename)
new_net_filename_linux = new_net_filenames[0]
new_net_filename_wine = new_net_filenames[1]
run_netlist(new_net_filename_wine)

#read results
raw_filename = new_net_filename_linux.replace(".net",".raw")
print(raw_filename)
variable_values =  read_variables(raw_filename)

for variable_value in variable_values:
    print(variable_value)
        
