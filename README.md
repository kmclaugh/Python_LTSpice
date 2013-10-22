These are a simple set of hacks for allowing python to read, run and edit 
LTSpice netlists, read LTSpice .raw files. There are functions for parameter
swapping so that one could run the same circuit for many different inputs 
(for example digital circuits with digital inputs). 

Only confirmed to work for DC Operating point simulations.

Right now it is designed to work the LTSpice running on wine on Ubunut although
it should be easily translatable to other systems by changing the pahtes and 
editing the run_netlist.sh file.

See the source code for function and object descriptions and methods
