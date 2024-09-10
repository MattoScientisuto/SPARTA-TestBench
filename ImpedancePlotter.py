import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

directory = "C:\\Users\\sparta\\Documents"

plt.figure(figsize=(10, 6))

for i in range(1, 4):
    for j in range(1, 4):
        for depth in ['5cm', '15cm']:
            pattern = f"{i}x{j}_{depth}.csv"
            file_path = os.path.join(directory, pattern)
            if os.path.isfile(file_path):

                df = pd.read_csv(file_path)
                
                # Impedance calculation
                zr1 = df['Zr']
                zi1 = df['Zi'] * -1
                freq1 = df['freq']
                lfreq1 = np.log10(freq1)
                imp1 = np.log10(np.sqrt(zr1**2 + zi1**2))
                
                # All '5cm's are red, all '15cm's are blue
                color = 'red' if depth == '5cm' else 'blue' 
                plt.plot(lfreq1, imp1, label=f"{i}x{j}_{depth}", linestyle='solid', linewidth=2, color=color)

plt.xlim(1, 5)
plt.ylim(-1, 10)
plt.xlabel('10log(frequency) /Hz', fontsize=15)
plt.ylabel('10log|Z| /ohm', fontsize=15)

# Wet Zone Horizontals
zone1_y = 4.3
zone2_y = 2.5
zone3_y = 0.5
plt.axhline(y=zone1_y, color='black', linestyle='--', linewidth=1.5)
plt.axhline(y=zone2_y, color='black', linestyle='--', linewidth=1.5)
plt.axhline(y=zone3_y, color='black', linestyle='--', linewidth=1.5)
plt.text(4.7, 6.2, 'Zone 4', color='r', ha='center', va='center', fontsize=12, weight='bold')
plt.text(4.7, 3.45, 'Zone 3', color='b', ha='center', va='center', fontsize=12, weight='bold')
plt.text(4.7, 1.4, 'Zone 2', color='g', ha='center', va='center', fontsize=12, weight='bold')
plt.text(4.7, -0.5, 'Zone 1', color='purple', ha='center', va='center', fontsize=12, weight='bold')

plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
plt.grid(True)
plt.title('Mars Yard DSP (8-1-2024)', fontsize=20, weight='bold')
plt.show()
