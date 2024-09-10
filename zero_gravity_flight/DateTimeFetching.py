# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Zero Gravity: General Date + Timestamp Fetcher

# Created: September 4th, 2024
# Last Updated: September 4th, 2024
# ============================================ #

from datetime import date, datetime

# Fetch timestamp
def get_timestamp():
    timestamp = datetime.now().strftime("%H:%M:%S")
    return timestamp
# Fetch dashed timestamp for file names
def get_dashedtime():
    dashed_time = datetime.now().strftime("%H-%M-%S")
    return dashed_time


# Fetch date stamp
def get_datestamp():
    datestamp = date.today().strftime("%m-%d-%Y")
    return datestamp


# Print general messages with a timestamp
def time_print(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f'[{timestamp}] {message}')
    # return f'[{timestamp}] {message}'


