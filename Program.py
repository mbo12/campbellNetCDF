import sys
import re
import __future__
import math
""" This module contains functions for parsing the text of a CRBASIC program"""
constants = {}
variables=[]

CRBASICtoPython = {'ACOS':'math.acos',
'ASIN':'math.asin',
'ATN':'math.atan',
'ATN2':'math.atan2',
'COS':'math.cos',
'COSH':'math.cosh',
'SIN':'math.sin',
'SINH':'math.sinh',
'TAN':'math.tan',
'TANH':'math.tanh',
'ABS':'abs',
'Ceiling':'math.ceil',
'EXP':'math.exp',
'Floor':'math.floor',
'INT':'math.floor',
'FIX':'math.floor',
'INTDV':'//',
'LN':'math.log',
'LOG':'math.log',
'LOG10':'math.log10',
'MOD':'%',
'PWR':'math.pow',
'Round':'round',
'Sqr':'math.sqrt'}




"""Delete all comments and return modified program text.
In CRBasic, comments begin with ' and end at end of line"""
def removeCommentedText (towerProgram):
  ### Does not preserve original line count
  progWithoutComments = ""
  for line in towerProgram.splitlines():
    # keep everything until first '
    lineToKeep = re.search(r"^([^'])+", line)
    if lineToKeep:
      if re.search(r'^\s*$', lineToKeep.group()): continue
      # in case chomped, sep with a newline character
      progWithoutComments = '\n'.join([progWithoutComments, lineToKeep.group()])
  return progWithoutComments    

def findNumericValueForString(str):
  str = substituteConstants(str)
  try: 
    ### send flag so no loss of precision when using eval
    result = eval(compile(str, '<string>', 'eval', __future__.division.compiler_flag))
  except:
    str = substituteMathOperators(str)
    result = eval(compile(str, '<string>', 'eval', __future__.division.compiler_flag))
  return result


def substituteConstants(text):
  keys = constants.keys()
  keys.sort(key=len, reverse=True)
  for name in keys:
    text = re.sub(name, constants[name], text)
  return text
  

def substituteMathOperators(text):
  for operator in CRBASICtoPython:
    text = re.sub(r'^'+operator+r'\s*'+r'(\()', CRBASICtoPython[operator]+r'\1', text)
    text = re.sub(r'(\s|/|\*|\+|\-|\=)'+operator+r'\s*'+r'(\()', r'\1'+CRBASICtoPython[operator]+r'\2', text)
  return text
  
    
""" Create dictionary of variable aliases"""
def getAliases (towerProgram):
  aliases = {}
  for line in towerProgram.splitlines():
    alias = re.search(r'^\s*Alias\s*(.*?)\s*=\s*(.*?)\s*$', line)
    if alias:   
      aliases[alias.group(1)] = alias.group(2)
  return aliases

def getVariables(towerProgram):
  for line in towerProgram.splitlines():
    var = re.search(r'^\s*(?:Public|Dim)\s*([^\s]+(\s*\(.*\))?)', line)
    if var:
      variables.append(var.group(1))
  adjustForArrayVars()

def adjustForArrayVars():
  for j in variables:
    var = substituteConstants(j)
    array=re.search(r'^([^\s])\s*\((\d+)\)', var)
    if array:
      for f in range(int(array.group(2))):
        variables.append(array.group(1)+'(%s)'%str(f+1))
      variables.remove(j)



### Put program constants in a dictionary  
def getConstants (towerProgram):
  for line in towerProgram.splitlines():
    constant = re.search(r'^\s*Const\s*(.*?)\s*=\s*(.*?)\s*$', line)
    if constant:
      numeric = re.search(r'^\d+\.?\d*$', constant.group(2))
      if not numeric:
        const = findNumericValueForString(constant.group(2))
        constants[constant.group(1)] = str(const)
      else: 
        constants[constant.group(1)] = constant.group(2)
  return constants
      


### Dictionary of units    
def getUnits(towerProgram):
  units = {}
  for line in towerProgram.splitlines():
    unit = re.search(r'^\s*Units\s*(.*?)\s*=\s*(.*?)\s*$', line)
    if unit:
      units[unit.group(1)] = unit.group(2)
  return units


""" return array of lines in table.  Each element in array is a string of 
table text."""
def getTables(towerProgram):
  towerProgram = towerProgram.splitlines()
  tables = []
  j = 0
  while j < len(towerProgram):
    line = towerProgram[j]
    startTable = re.search(r'^\s*DataTable\s*\((.*?)\)', line)
    if startTable:
      table = line
      j+=1
      while not re.search(r'^\s*EndTable', towerProgram[j]):
        table = '\n'.join([table, towerProgram[j]])
        j+=1
      tables.append(table)
    j+=1
  return tables

def main():
  ### test case on flux.cr3
  with open('flux.cr3', 'r') as f:
    text = f.readlines()
  text = removeCommentedText(text)
  
  getConstants(text)
  v = getVariables(text)
  tables = getTables(text)


  

if __name__ == '__main__':
  main()
