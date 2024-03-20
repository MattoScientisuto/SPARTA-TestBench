# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Blue Origin DSP Sequence: NI Device Loader Service Starter

# Created: March 20th, 2024
# Last Updated: March 20th, 2024
# ============================================ #

import subprocess

def enable_and_start_service(service_name):
    try:
        # Using sc.exe command to enable the service and start it
        subprocess.run(['sc', 'config', service_name, 'start=auto'], check=True)
        subprocess.run(['sc', 'start', service_name], check=True)
        print(f"Service '{service_name}' has been enabled and started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to enable and start service '{service_name}': {e}")

# Example usage
enable_and_start_service("nidevldu")