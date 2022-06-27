#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 20:10:20 2021

@author: robertclay

File to take LAD codes from BHPS rtf format data dictionary.
"""

from docx import Document # to read docx
import re #regex
import pandas as pd

file = "/Users/robertclay/Documents/6614stata_471A424C959CCFC9AE423A866B5794B9_V1/UKDA-6614-stata/mrdoc/ukda_data_dictionaries/bhps_w1/ba_indresp_ukda_data_dictionary.docx"

doc = Document(file)
# Extract document and put it in a list where each row is an element
text = [item.text for item in doc.paragraphs]
# cut off the desired data dictionary of LADs
text = text[172 : 516]

id_to_LAD_name = {}

for item in text:
    # find the intiger value code and name of each LAD using regex. Store them in a dictionary.
    LAD_value = re.search("\tValue = (.+?).0\t", item).group(1)
    LAD_value = int(LAD_value)
    LAD_name = re.search("\tLabel = (.*)", item).group(1)
    
    #LAD_name_to_id[LAD_name] = LAD_value
    id_to_LAD_name[LAD_value] = LAD_name
    
# Bunch of corrections for names that are different between BHPS LAD codes and NOMIS 2019 Mortality LAD codes.
# Mostly due to administrative changes to counties over time. E.g. bath and north somerset split.

id_to_LAD_name[1] = 'Westminster'
id_to_LAD_name[4] = 'Hammersmith and Fulham'
id_to_LAD_name[7] = 'Kensington and Chelsea'
id_to_LAD_name[45] = 'St. Helens'
id_to_LAD_name[69] = 'Bath and North East Somerset'
id_to_LAD_name[70] = 'Bristol, City of'
id_to_LAD_name[71] = 'Stroud'
id_to_LAD_name[72] = 'North Somerset'




# invert dictionary for later. need to go from intiger to name to LAD code. 
# this is current from name to intiger
LAD_name_to_id = {}
for value in id_to_LAD_name.keys():
    name = id_to_LAD_name[value]
    LAD_name_to_id[name] = value 

# now load in the LAD data to convert intigers to the actual LAD codes.

LAD_code_data = pd.read_csv("/Users/robertclay/Documents/Output_Area_to_LSOA_to_MSOA_to_Local_Authority_District__December_2017__Lookup_with_Area_Classifications_in_Great_Britain.csv")

LAD_names = list(set(LAD_code_data["LAD17NM"]))
LAD_codes = list(set(LAD_code_data["LAD17CD"]))

name_to_LAD_code = {}

for i, item in enumerate(LAD_names):
    #value = id_to_LAD_name[item]
    code = LAD_codes[i]
    name_to_LAD_code[item] = code
    
    
# final part link intiger codes in bhps to LAD code.


id_to_LAD_codes = {}
for item in LAD_name_to_id.keys():
    
    value = LAD_name_to_id[item]
    code = name_to_LAD_code[item]
    
    id_to_LAD_codes[value] = code
    
    

