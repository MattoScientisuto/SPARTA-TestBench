# SPARTA Test Bench
Python interface software for the SPARTA (Soil Properties Assessment Resistance and Thermal Analysis) test bench. Currently automates the reading, logging, and real-time visualization of data from a load cell, torque sensor, and dielectric spectrometer.
This interface is being developed for my current intern project managed by NASA Jet Propulsion Laboratory under Division 32 (Planetary Science).

<h3>Dependencies / Imports:</h3>

 - Matplotlib
 - NI-DAQmx
 - pandas
 - Pillow
 - pyvium
 - serial
 - Thread
 - Tkinter
 - subprocess
 - psutil
 - socket

<h3>Start-up</h3>

To open the GUI in a terminal, use:
```
python GUI_Bench.py
```

To open the GUI without a terminal, use:
```
start.bat
```

<h2>In order to run tests on any bench component:</h2>

<h3>Data Acquisition</h3>

**National Instruments:** cDAQ 9174 + DAQ 9237 must be connected to your PC with USB
 - a0 slot is for the Load Cell RJ50 cable adapter : (MLP-100 or SSM-100 from **Transducer Techniques**)
 - a1 slot is for the Torque Sensor RJ50 cable adapter : (RTS-200 from **Transducer Techniques**)

**Ivium:** PocketStat2 must be connected with USB
 - IviumSoft must also be installed and open for Di-electric Spectrometer connection and testing


<h3>Hardware Operations</h3>

**Firgelli Automation:** Linear Actuator (6 inch length)
 - Connect to a power supply, giving at most 12 VDC
 - For our purposes, 3 Volts provides the optimal velocity

**Anaheim Automation:** PCL601USB + MBC25081TB Stepper Motor Controller must be connected with USB
 - Connected to a power supply giving at most 24 VDC

<h2>Blue Origin Operation Sequence:</h2>

To start the sequence, use:
```
startBlueOriginDSP_fullpaths.bat
```

**Ivium:** Four PocketStat2 DSPs must be connected with USB to the micro PC USB hub
  - Script is designed to continuously run all four simultaneously while in flight
  - Estimated to be running for about 6 hours

**Intertial Labs:** IMU-P must be connected with USB to the micro PC USB hub
  - Designed to be ran through a LabView executable
  - Will run simultaneously to the DSPs
