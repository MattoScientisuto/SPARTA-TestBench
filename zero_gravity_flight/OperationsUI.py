# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA  
# Zero Gravity: Operations Interface

# Created: September 10th, 2024
# Last Updated: September 23th, 2024
# ============================================ #

from LivePlots import *
from RotateMotor import *

import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import atexit

# log_path = f"C:\\zero_gravity_output\\console_log_geomechanical.txt"
# os.makedirs(os.path.dirname(log_path), exist_ok=True)
# sys.stdout = open(log_path, "a")


root = tk.Tk()
root.title('SPARTA: Zero Gravity Geomechanical Operations')
root.geometry('1030x800')

imagehead_frame = Frame(root, width=200, height=root.winfo_height())
imagehead_frame.grid(row=0, column=0, columnspan=3)
header_frame = Frame(root, width=200, height=root.winfo_height())
header_frame.grid(row=1, column=0, columnspan=3)
cpt_frame = Frame(root, width=200, height=root.winfo_height())
cpt_frame.grid(row=2, column=0)
vst_frame = Frame(root, width=200, height=root.winfo_height())
vst_frame.grid(row=2, column=1)
dsp_frame = Frame(root, width=200, height=root.winfo_height())
dsp_frame.grid(row=3, column=0, columnspan=3)

jpl_logo = Image.open('C:\\Users\\sparta\\Desktop\\SPARTA-TestBench\\gui_images\\jpl_logo_resized.png')
jpl_img = ImageTk.PhotoImage(jpl_logo)
label1 = tk.Label(imagehead_frame,image=jpl_img)
label1.image = jpl_img
label1.grid(row=0, column=1, padx=5, pady=5)
main_title = tk.Label(header_frame, text="SPARTA: Zero Gravity\nGeomechanical Operations", font=("Arial", 18))
main_title.grid(row=1, column=1, padx=5, pady=5, sticky=NW) 


cpt_op = tk.Button(cpt_frame, text="CPT Operation", command=start_cpt_thread)
cpt_op.grid(row=0, column=1, pady=5)
cpt_reset = tk.Button(cpt_frame, text="CPT Reset", command=reset_cpt_thread)
cpt_reset.grid(row=1, column=1, pady=5)

vst_op = tk.Button(vst_frame, text="VST Operation", command=start_vst_thread)
vst_op.grid(row=0, column=1, pady=5)
vst_reset = tk.Button(vst_frame, text="VST Reset", command=reset_vst_thread)
vst_reset.grid(row=1, column=1, pady=5)


# CPT
canvas = FigureCanvasTkAgg(fig1, master=cpt_frame)
canvas.get_tk_widget().grid(row=2, column=0, columnspan=3, padx=30, pady=20)
canvas.get_tk_widget().config(borderwidth=2, relief=tk.GROOVE)

# VST
canvas2 = FigureCanvasTkAgg(fig2, master=vst_frame)
canvas2.get_tk_widget().grid(row=2, column=0, columnspan=3, padx=30, pady=26)
canvas2.get_tk_widget().config(borderwidth=2, relief=tk.GROOVE)

ani = FuncAnimation(fig1, animate_load_cell, interval=500, cache_frame_data=False)
ani2 = FuncAnimation(fig2, animate_torque_sensor, interval=500, cache_frame_data=False)


# ===

# Automatically closes serial ports as soon as the program is closed
def exit_handler():
    if linear_actuator.isOpen() == True:
        linear_actuator.close()
        print("Linear Actuator Port Status: ", linear_actuator.isOpen())
        print("Linear Actuator port closed successfully!")
    else:
        print("Linear Actuator already closed")

    if stepper.isOpen() == True:
        stepper.close()
        print("Torque Motor Port Status: ", stepper.isOpen())
        print("Torque Motor port closed succesfully!")
    else:
        print("Torque Motor already closed")

    sys.stdout.close()

atexit.register(exit_handler)

root.mainloop()