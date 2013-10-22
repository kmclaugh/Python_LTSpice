#!/bin/bash
source ~/.bashrc
cd $C_DRIVE
cd Program\ Files/LTC/LTspiceIV
wine scad3.exe -ascii -b -run $1

