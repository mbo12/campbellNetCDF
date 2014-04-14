import xml.dom.minidom
import sys 
from xmlutils import getText
import re
""" This module contains functions for parsing a programxml """

def isProgXML(file):
  if re.search(r'\.cr\d\.xml$',file,flags=re.IGNORECASE):
    return True
  
def parseXML (fileName,tableName):
  ### return a hashtable with columns and variable names
  table = _findTable(fileName,tableName)
  variables = {}
  varNodes = table.getElementsByTagName("variable")
  for node in varNodes:
    varName = node.getElementsByTagName("varName")
    column = node.getElementsByTagName("tableColumn")
    variables[varName[0].childNodes[0].data] = column[0].childNodes[0].data
  return variables

def varsToRead(table):
  toRead = {}
  var = table.getElementsByTagName("variable")
  for v in var:
    name = getText(v,"varName")
    col = getText(v,"tableColumn")
    toRead[name] = col
  return toRead
  
def recordsInDay(fileName,tableName):
  """ return how many records to allocate per day"""
  table = _findTable(fileName,tableName)
  interval = table.getElementsByTagName("outputInterval")
  return interval[0].childNodes[0].data


def _findTable (fileName,tableName):
  progXML = xml.dom.minidom.parse(fileName)
  tables = progXML.getElementsByTagName("table")
  for table in tables:
    tableNameNode = table.getElementsByTagName("tableName")
    if tableNameNode[0].childNodes[0].data == tableName:
      return table
  ## we shouldn't get here...
  raise Exception('could not find table "' + tableName + '" in ' + fileName)
  
  
def main ():
  print recordsInDay("MainTowerCR3000_ground_v8.cr3.xml","Table1")
  
  
if __name__ == '__main__':
  main()
