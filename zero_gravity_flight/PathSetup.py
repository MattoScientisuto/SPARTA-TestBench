# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Zero Gravity: Subfolder Path Setup

# Created: October 7th, 2024
# Last Updated: October 7th, 2024
# ============================================ #

import sys
import os

# Get the path to the parent folder (SPARTA-TestBench)
parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent folder to sys.path so modules within 'zero_gravity_flight' can access other subfolders in the parent
sys.path.append(parent_folder)