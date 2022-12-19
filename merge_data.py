
##Import modules
import re
import pandas as pd
import numpy as np
import os

# let's make a list compreension for all the data in the folder
files = [file for file in os.listdir('sales_final/')] 

# let's make a pandas DataFrame
all_data = pd.DataFrame()

# makes a loop for concat the data
for file in files:
    data = pd.read_csv("sales_final/" + file)
    all_data = pd.concat([all_data, data])

# export all data to csv    
all_data.to_csv("data/sales_data.csv", index=False)

print("Merge Completed")
 
