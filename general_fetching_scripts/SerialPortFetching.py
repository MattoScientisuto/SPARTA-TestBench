# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Serial Port Fetching

# Created: October 7th, 2024
# Last Updated: October 7th, 2024
# ============================================ #

import serial.tools.list_ports


# List all connected COM ports and their details
def list_ports():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        print(f"Device: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  VID: {hex(port.vid) if port.vid else 'N/A'}")
        print(f"  PID: {hex(port.pid) if port.pid else 'N/A'}")
        print(f"  Serial Number: {port.serial_number if port.serial_number else 'N/A'}")
        print(f"  Manufacturer: {port.manufacturer}")
        print(f"  Location: {port.location}")
        print(f"  HWID: {port.hwid}")
        print("-" * 30)


# Find the device port name and return it
def find_device(vendor_id, product_id, serial_number=None):

    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if (hex(port.vid) == vendor_id and hex(port.pid) == product_id):
            if serial_number is None or port.serial_number == serial_number:
                return port.device  # Returns the COM port (e.g., 'COM14')
    return None


# COM device dictionaries so pyserial knows what to look for
usb_linear_actuator = {
    'vendor_id': '0x2341', 
    'product_id': '0x43', 
    'serial_number': '34333323932351716191'
}

usb_rotate_motor = {
    'vendor_id': '0x403',  
    'product_id': '0x6001'
}

# Find the COM port for each device
linear_actuator_com = find_device(usb_linear_actuator['vendor_id'], usb_linear_actuator['product_id'], usb_linear_actuator.get('serial_number'))
rotate_motor_com = find_device(usb_rotate_motor['vendor_id'], usb_rotate_motor['product_id'], usb_rotate_motor.get('serial_number'))

# list_ports()
if linear_actuator_com:
    print(f"Linear Actuator Arduino is at: {linear_actuator_com}")
else:
    print("ERROR: Linear Actuator Arduino was not not found.")

if rotate_motor_com:
    print(f"Rotation Motor is at: {rotate_motor_com}\n")
else:
    print("ERROR: Rotation Motor not found.")
