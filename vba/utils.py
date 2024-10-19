#%%

# make sure all .bas files start with
# Attribute VB_Name = <name of the file>

import os
from tqdm import tqdm

#%%
# get all .bas files in 'original' folder
bas_files = [f for f in os.listdir('original') if f.endswith('.bas')]
# add the path 
bas_files = ['original/' + f for f in bas_files]
# loop and read all .bas files, check the first line 
for f in bas_files:
    with open(f, 'r') as file:
        first_line = file.readline().strip()

    line_to_add = None
    if first_line.startswith('Attribute VB_Name'):
        # remove the first line 
        with open(f, 'r') as file:
            lines = file.readlines()
        with open(f, 'w') as file:
            file.writelines(lines[1:])
            

# file by file 

# %%
# go through all of those files and add all the text into
# Module1.bas (not in original folder)
with open('Module1.bas', 'w') as file:
    for f in tqdm(bas_files):
        with open(f, 'r') as file2:
            lines = file2.readlines()
        file.writelines(lines)