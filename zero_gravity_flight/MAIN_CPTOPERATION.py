# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Zero Gravity: CPT Reset

# Created: September 9rd, 2024
# Last Updated: September 9th, 2024
# ============================================ #
from DateTimeFetching import *
from SensorOps import *

import time


# =========================
# Sequence of Operations
# =========================

if __name__ == "__main__":
    time.sleep(3)
    cpt = start_cpt_thread()
    cpt.join()
    vst = start_vst_thread()
    vst.join()

    r1 = reset_cpt_thread()
    r1.join()
    r2 = reset_vst_thread()
    r2.join()