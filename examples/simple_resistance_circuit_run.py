#!/usr/bin/python
## Simple demo of the python_ltspice_tools
## Changes the simple_resistance_circuit.net resistance parameters, and prints the test node result
from python_ltspice_tools import *

#Read netlist file into the netlist object
original_filename = "/home/kevin/.wine/drive_c/Program Files/LTC/LTspiceIV/Python_LTSpice_Examples/simple_resistance_circuit.net"
original_netlist = netlist_class(original_filename)

#Change the resistance parameters
change_params = {"Rload0":"1k","Rload1":"5k"}
new_netlist = original_netlist.change_parameters(change_params)

#Run the new netlist and store the results in a raw_value object
new_raw_values = new_netlist.run_netlist()

#Look up the test node a print its value
test_node = new_raw_values.return_node_value("test")
print(test_node)


