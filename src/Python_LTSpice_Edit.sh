#!/bin/bash
source ~/.bashrc
cd $C_DRIVE
cd Program\ Files/LTC/LTspiceIV
wmctrl -o  $DX0,$DY1
nautilus .
sleep 3
wmctrl -o  $DX1,$DY1
wine scad3.exe Python_LTSpice_Examples/simple_resistance_circuit.asc
sleep 7
wmctrl -o  $DX1,$DY0
gvim -p ~/Projects/Python_LTSpice/src/Python_LTSpice_Edit.sh ~/Projects/Python_LTSpice/src/python_ltspice_tools.py ~/Projects/Python_LTSpice/examples/simple_resistance_circuit_run.py
#End

