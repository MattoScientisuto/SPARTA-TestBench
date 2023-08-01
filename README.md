# SPARTA Test Bench
Interface software for SPARTA test bench

Dependencies / Imports:
 - Matplotlib
 - NI-DAQmx
 - pandas
 - PIL
 - pyvium
 - Thread
 - Tkinter

To open in a terminal, use:
```
python GUI_Bench.py
```

In order to run tests on any bench component:

cDAQ 9174 + DAQ 9237 must be connected to your PC with USB
 - a0 slot is for the Load Cell RJ50 cable
 - a1 slot is for the Torque Sensor RJ50 cable

Ivium PocketStat2 must be connected with USB
 - IviumSoft must also be installed and open for DSP connection and testing
