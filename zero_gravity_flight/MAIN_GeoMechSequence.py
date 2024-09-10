# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Zero Gravity: Main Driver Sequence

# Created: September 3rd, 2024
# Last Updated: September 4th, 2024
# ============================================ #
from DateTimeFetching import *
from SensorOps import *

import time
from datetime import date, datetime
import datetime as dt

# Redirect all operation prints to a text file
# sys.stdout = open("ZeroG_OperationsLog.txt", "a")


# =========================
# Sequence of Operations
# =========================

if __name__ == "__main__":

    print(f'============================================================================================================\nMAIN LOG {get_datestamp()} at {get_timestamp()}')

    # # Start CPT Operation 
    # # .join() will ensure the next thread will not start until the previous one is finished
    # thread1 = start_cpt_thread()
    # thread1.join()

    # # Start VST Operation
    # thread2 = start_vst_thread()
    # thread2.join()

    # # Small delay before reset to make sure everything settles
    # time.sleep(2)

    # reset1 = reset_cpt_thread()
    # reset1.join()
    # time_print('CPT reset done')
    # time.sleep(1)
    # reset2 = reset_vst_thread()
    # reset2.join()
    # time_print('CPT reset done')

    # linear_actuator.close()
    # stepper.close()
    # # sys.stdout.close()

    start_vst_thread()