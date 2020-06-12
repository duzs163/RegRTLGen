#!/usr/bin/python

import sys
import os
import string
import re
import time
import subprocess
import datetime
from sys import argv

# import library
script_path = os.path.dirname(__file__)
lib_path = script_path + "/../../lib/pyLib"
sys.path.append(lib_path)
from RegSpec import RegSpec

# in RegSpec[RegSpec_*]['Common_Config'] = {}
normal_variables = ["GenModuleName", "GenWProtParam", "GenWProtErrParam", "GenSecParam", "GenSecErrParam", "GenAsyncParam", "GenSyncStageParam", "GenAddrParam", "GenDataParam"]
normal_conditions = ["GenWProtParam", "GenAsyncReset", "GenSyncReset"]

# sub function
def normal_variables_replace(line):
  for variable in normal_variables:
    if variable in line:
      chosen_variable = re.escape("$" + variable) # variable -> \$variable
      line = re.sub(chosen_variable, RegSpec[spec_sheet]['Common_Config'][variable], line)
  return line
  
## Main process
line_print = ''
for spec_cnt in range(1, len([*RegSpec])):
  # prepare output RTL
  spec_sheet = [*RegSpec][spec_cnt]
  output_path = script_path + "/../../output/" + RegSpec[spec_sheet]['Common_Config']['GenModuleName'] + ".sv"
  rtl_output = open(output_path, "w")
  
  # read sample RTL
  sample_path = script_path + "/../../lib/rtlLib/RegGen_ApbIf.sv"
  rtl_sample = open(sample_path, "r")
  lines = rtl_sample.readlines()
  
  loop_flag = 0
  for line in lines:
    if loop_flag != 0:
      if '$GenEndLoop' in line:
        loop_block.close()
        loop_block = open("loop_block_temp", "r")
        lines_temp = loop_block.readlines()
        
        if loop_flag == 3:
          for reg_cnt in range(1, len([*RegSpec[spec_sheet]])):
            reg_key = [*RegSpec[spec_sheet]][reg_cnt]
            for field_cnt in range(1, len([*RegSpec[spec_sheet][reg_key]])):
              field_key = [*RegSpec[spec_sheet][reg_key]][field_cnt]
              for split_cnt in range(1, len([*RegSpec[spec_sheet][reg_key][field_key]])):
                split_key = [*RegSpec[spec_sheet][reg_key][field_key]][split_cnt]

                for line_temp in lines_temp:
                  print_flag = 0
                  first_element = line_temp.split()[0] # get first element of line_temp
                  if '$GenNOT' in first_element:
                    print_flag = 1 # default is print, met condition to not print
                    first_element = first_element.replace('$GenNOT', '') # remove $GenNOT
                    line_temp = line_temp.replace('$GenNOT', '') # remove $GenNOT
                    
                    list_condition = re.escape(first_element) # backslash: $first_element -> \$first_element
                    line_temp = re.sub(list_condition, "", line_temp) # keep rtl code, remove list_condition
                    match_condition = 0
                    
                    condition_array = first_element.replace('$', ' ').strip().split() # remove $, split into array
                    for condition in condition_array: # check all RW property
                      if condition in RegSpec[spec_sheet][reg_key][field_key][split_key]['RW_Property']:
                        match_condition = 1
                        print_flag = 0
                        break
                  elif '$Gen' in first_element: # first element is normal condition for gen or not gen
                    condition = re.escape(first_element) # backslash: $first_element -> \$first_element
                    line_temp = re.sub(condition, "", line_temp) # keep rtl code, remove condition
                    
                    condition = condition.replace('\$','')
                    if condition in normal_conditions:
                      if RegSpec[spec_sheet]['Common_Config'][condition] == "0": # condition = 0, not gen
                        continue
                  elif '$' in first_element:
                    list_condition = re.escape(first_element) # backslash: $first_element -> \$first_element
                    line_temp = re.sub(list_condition, "", line_temp) # keep rtl code, remove list_condition
                    match_condition = 0
                    
                    condition_array = first_element.replace('$', ' ').strip().split() # remove $, split into array
                    for condition in condition_array: # check all RW property
                      if condition in RegSpec[spec_sheet][reg_key][field_key][split_key]['RW_Property']:
                        match_condition = 1
                        print_flag = 1
                        break
                  else:
                    print_flag = 1
                    
                  if print_flag == 1:
                    if '$GenRegName' in line_temp:
                      line_temp = line_temp.replace('$GenRegName', RegSpec[spec_sheet][reg_key]['Common_Config']['GenRegName'])
                    if '$GenRegField' in line_temp:
                      line_temp = line_temp.replace('$GenRegField', RegSpec[spec_sheet][reg_key][field_key]['Common_Config']['GenRegField'])
                    if '$GenPartialBitRange' in line_temp:
                      line_temp = line_temp.replace('$GenPartialBitRange', RegSpec[spec_sheet][reg_key][field_key][split_key]['GenPartialBitRange'])
                    if '$GenFieldReset' in line_temp:
                      line_temp = line_temp.replace('$GenFieldReset', RegSpec[spec_sheet][reg_key][field_key][split_key]['GenFieldReset'])
                    if '$GenPStrbIndex' in line_temp:
                      line_temp = line_temp.replace('$GenPStrbIndex', RegSpec[spec_sheet][reg_key][field_key][split_key]['GenPStrbIndex']) 
                    if '$Gen' in line_temp: # has normal variables to be replaced
                      line_temp = normal_variables_replace(line_temp)
                    line_print += line_temp  
        elif loop_flag == 2:
          for reg_cnt in range(1, len([*RegSpec[spec_sheet]])):
            reg_key = [*RegSpec[spec_sheet]][reg_cnt]
            for field_cnt in range(1, len([*RegSpec[spec_sheet][reg_key]])):
              field_key = [*RegSpec[spec_sheet][reg_key]][field_cnt]
              
              for line_temp in lines_temp:
                print_flag = 0
                first_element = line_temp.split()[0] # get first element of line_temp
                if '$GenNOT' in first_element:
                  print_flag = 1 # default is print, met condition to not print
                  first_element = first_element.replace('$GenNOT', '') # remove $GenNOT
                  line_temp = line_temp.replace('$GenNOT', '') # remove $GenNOT
                  
                  list_condition = re.escape(first_element) # backslash: $first_element -> \$first_element
                  line_temp = re.sub(list_condition, "", line_temp) # keep rtl code, remove list_condition
                  match_condition = 0
                  
                  condition_array = first_element.replace('$', ' ').strip().split() # remove $, split into array
                  for condition in condition_array: # check all RW property
                    if condition in RegSpec[spec_sheet][reg_key][field_key]['Common_Config']['RW_Property']:
                      match_condition = 1
                      print_flag = 0
                      break
                elif '$Gen' in first_element: # first element is normal condition for gen or not gen
                  condition = re.escape(first_element) # backslash: $first_element -> \$first_element
                  line_temp = re.sub(condition, "", line_temp) # keep rtl code, remove condition
                  
                  condition = condition.replace('\$','')
                  if condition in normal_conditions:
                    if RegSpec[spec_sheet]['Common_Config'][condition] == "0": # condition = 0, not gen
                      continue
                elif '$' in first_element:
                  list_condition = re.escape(first_element) # backslash: $first_element -> \$first_element
                  line_temp = re.sub(list_condition, "", line_temp) # keep rtl code, remove list_condition
                  match_condition = 0
                  
                  condition_array = first_element.replace('$', ' ').strip().split() # remove $, split into array
                  for condition in condition_array: # check all RW property
                    if condition in RegSpec[spec_sheet][reg_key][field_key]['Common_Config']['RW_Property']:
                      match_condition = 1
                      print_flag = 1
                      break
                else:
                  print_flag = 1
                
                if print_flag == 1:
                  if '$GenRegName' in line_temp:
                    line_temp = line_temp.replace('$GenRegName', RegSpec[spec_sheet][reg_key]['Common_Config']['GenRegName'])
                  if '$GenRegField' in line_temp:
                    line_temp = line_temp.replace('$GenRegField', RegSpec[spec_sheet][reg_key][field_key]['Common_Config']['GenRegField'])
                  if '$Gen' in line_temp: # has normal variables to be replaced
                    line_temp = normal_variables_replace(line_temp)
                  line_print += line_temp
        elif loop_flag == 1:
          for reg_cnt in range(1, len([*RegSpec[spec_sheet]])):
            reg_key = [*RegSpec[spec_sheet]][reg_cnt]
            
            for line_temp in lines_temp:
              print_flag = 0
              first_element = line_temp.split()[0] # get first element of line_temp
              if '$GenNOT' in first_element:
                print_flag = 1 # default is print, met condition to not print
                first_element = first_element.replace('$GenNOT', '') # remove $GenNOT
                line_temp = line_temp.replace('$GenNOT', '') # remove $GenNOT
                
                list_condition = re.escape(first_element) # backslash: $first_element -> \$first_element
                line_temp = re.sub(list_condition, "", line_temp) # keep rtl code, remove list_condition
                match_condition = 0
                
                condition_array = first_element.replace('$', ' ').strip().split() # remove $, split into array
                if '$GenPStrbIndex' in line_temp: # sample line got $GenPStrbIndex -> need to clone
                  line_temp_total = ''
                  for strobe_cnt in range (0, len([*RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property']])):
                    strobe_key = [*RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property']][strobe_cnt]
                    line_temp_each = line_temp
                    line_temp_each = line_temp_each.replace('$GenPStrbIndex', str(strobe_cnt)) # clone strobe line from sample line
                    for condition in condition_array:
                      if condition in RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property'][strobe_key]:
                        match_condition = 1
                        break
                    if match_condition == 0:
                      line_temp_total += line_temp_each # strobe line can print out
                    else:
                      match_condition = 0 # reset check flag
                  if line_temp_total != '':
                    line_temp = line_temp_total # replace sample line after check each strobe
                  else:
                    print_flag = 0
                else:
                  for condition in condition_array: # check all RW property
                    for strobe_cnt in range (0, len([*RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property']])):
                      strobe_key = [*RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property']][strobe_cnt]
                      if condition in RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property'][strobe_key]:
                        match_condition = 1
                        break
                    if match_condition == 1:
                      print_flag = 0
                      break
              elif '$Gen' in first_element: # first element is normal condition for gen or not gen
                condition = re.escape(first_element) # backslash: $first_element -> \$first_element
                line_temp = re.sub(condition, "", line_temp) # keep rtl code, remove condition
                
                condition = condition.replace('\$','')
                if condition in normal_conditions:
                  if RegSpec[spec_sheet]['Common_Config'][condition] == "0": # condition = 0, not gen
                    continue
              elif '$' in first_element:
                list_condition = re.escape(first_element) # backslash: $first_element -> \$first_element
                line_temp = re.sub(list_condition, "", line_temp) # keep rtl code, remove list_condition
                match_condition = 0
                
                condition_array = first_element.replace('$', ' ').strip().split() # remove $, split into array
                if '$GenPStrbIndex' in line_temp: # sample line got $GenPStrbIndex -> need to clone
                  line_temp_total = ''
                  for strobe_cnt in range (0, len([*RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property']])):
                    strobe_key = [*RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property']][strobe_cnt]
                    line_temp_each = line_temp
                    line_temp_each = line_temp_each.replace('$GenPStrbIndex', str(strobe_cnt)) # clone strobe line from sample line
                    for condition in condition_array:
                      if condition in RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property'][strobe_key]:
                        line_temp_total += line_temp_each # strobe line match condition to print out
                        break
                  if line_temp_total != '':
                    line_temp = line_temp_total # replace sample line after check each strobe
                    print_flag = 1  
                else:
                  for condition in condition_array: # check all RW property
                    for strobe_cnt in range (0, len([*RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property']])):
                      strobe_key = [*RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property']][strobe_cnt]
                      if condition in RegSpec[spec_sheet][reg_key]['Common_Config']['RW_Property'][strobe_key]:
                        match_condition = 1
                        break
                    if match_condition == 1:
                      print_flag = 1
                      break
              else:
                print_flag == 1
                
              if print_flag == 1:
                if '$GenRegName' in line_temp:
                  line_temp = line_temp.replace('$GenRegName', RegSpec[spec_sheet][reg_key]['Common_Config']['GenRegName'])
                if '$Gen' in line_temp: # has normal variables to be replaced
                  line_temp = normal_variables_replace(line_temp)
                line_print += line_temp
        loop_flag = 0
        continue
      else:
        loop_block.write(line) # store line in loop_block
        continue
    else:
      if '$GenStartLoop$GenRegName$GenRegField$GenPartialBitRange' in line:
        loop_flag = 3
        loop_block = open("loop_block_temp", "w")
        continue
      if '$GenStartLoop$GenRegName$GenRegField' in line:
        loop_flag = 2
        loop_block = open("loop_block_temp", "w")
        continue
      if '$GenStartLoop$GenRegName' in line:
        loop_flag = 1
        loop_block = open("loop_block_temp", "w")
        continue
      elif '$GenUserHeader' in line:
        line = line.replace('$GenUserHeader', RegSpec['GenUserHeader'])
      else: # normal line
        first_element = line.split()[0] # get first element of line
        if '$Gen' in first_element: # first element is normal condition for gen or not gen
          condition = re.escape(first_element) # backslash: $first_element -> \$first_element
          line = re.sub(condition, "", line) # keep rtl code, remove condition
          
          condition = condition.replace('\$','')
          if RegSpec[spec_sheet]['Common_Config'][condition] == "0": # condition = 0, not gen
            continue
        if '$Gen' in line: # has normal variables to be replaced
          line = normal_variables_replace(line)
    line_print += line
rtl_output.write(line_print) # write all content to output RTL

# finish
os.remove('loop_block_temp')
open("finish_gen_rtl", 'w').close()
