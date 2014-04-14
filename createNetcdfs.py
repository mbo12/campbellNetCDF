""" Make an empy netcdf file with space allocated for all of the tower 
variables."""
import xml.dom.minidom
import sys
import os
import re
import time
from netCDF4 import Dataset
from xmlutils import getText
from ParseProgXML import isProgXML
from xml.dom.minidom import parse

ROOTNAME = 'MpalaTower' # root name for netcdf file
### name will be ROOTNAME_YEAR_DOY.nc

### class for getting variable info from progxmls
class towerVariables ():
  def __init__(self):
    self.variables = {}
    self.varUnits = {}
    self.origNames = {} ## ie not alias name
    
  def addVar(self, interval, name):
    epoch = self.variables.get(interval)
    if epoch == None:
      self.variables[interval] = set()
      epoch = self.variables[interval]
    epoch.add(name)
  
  def addUnits(self, name, unit):
    self.varUnits[name] = unit

  def getUnits(self, name):
    return self.varUnits.get(name)
    
  def gen(self):
    for k in self.variables:
      yield k, self.variables[k]
  
  def addOrig (self, varName, origName):
    self.origNames[varName]=origName
  
  def getOrig (self, name):
    return self.origNames.get(name)
          
  def __iter__(self):
    return self.gen()
      


def addVariables (progXML, variables):
  ### get all variable names for each epoch in progxml
  tables = progXML.getElementsByTagName('table')
  for table in tables:
    interval = (getText(table, 'outputInterval'))
    if interval == 'None':
      interval = 1.0
    else:
      interval = float(interval)
    vars = table.getElementsByTagName('variable')
    for var in vars:
      name = getText(var, 'varName')
      variables.addVar(interval, name)
      ### metadata: get units
      units = getText(var, 'varUnits')
      if units:
        variables.addUnits(name, units)
      origName = getText(var, 'origName')
      ### original name (ie not alias. so as to match up with other metadata)
      if origName: 
        variables.addOrig(name, origName)
  return variables
        
def getObservations (obsXmlFile):
  obsXml = xml.dom.minidom.parse(obsXmlFile)
  ### get metadata from obsXml
  obsTypes = {}
  obsLimits = {}
  observations = obsXml.getElementsByTagName('observation')
  for obs in observations:
    obsName = getText(obs, 'obsName')
    varName = getText(obs, 'varName')
    minVal = getText(obs, 'minValue')
    maxVal = getText(obs, 'maxValue')
    obsTypes[varName] = obsName
    obsLimits[obsName] = (minVal, maxVal)
  return obsTypes, obsLimits
  
    
def makeEmptyNetcdf(filename, vars, obsTypes, obsLimits):
  ## make daily empty netcdf file for vars
 ## include metadata of obsTypes and obsLimits
  
  netcdf = Dataset(filename, 'w', format='NETCDF4')
  for epoch, var in vars:
    ## add group for epoch if it's not already in the netcdf file
    try:
      grp = netcdf.groups[groupName(epoch)]
    except:
      grp = netcdf.createGroup(groupName(epoch))
      ## time dimension: allocate space in file based on sampling interval
      dim = grp.createDimension('time', 24*60*60/epoch-1)
      grp.createVariable('dates', 'f8', ('time',))

    for v in var:
      varID = grp.createVariable(v, 'f8', ('time',))
      ### attributes from metadata
      u = vars.getUnits(v)
      if u: 
        varID.units = u
      if v in obsTypes:
        obsName = obsTypes[v]
        writeObsAttributes(varID, obsName, obsLimits[obsName])
      elif vars.getOrig(v):
        if vars.getOrig(v) in obsTypes:
          obsName = obsTypes[vars.getOrig(v)]
          writeObsAttributes(varID, obsName, obsLimits[obsName])
  netcdf.close()

def writeObsAttributes(varID, obsName, obsLimits):
  varID.obsName = obsName
  ### add limits if defined
  if obsLimits[0] != None:
    varID.minVal = obsLimits[0]
  if obsLimits[1] != None:
    varID.maxVal = obsLimits[1]
    
    
def fileName(year, doy):
  return ROOTNAME + '_%d_%03d.nc' % (year, doy)

def groupName(epoch):
  ## based on sampling period define epoch name
  ## if sampling period < 1 min, define in Hz (freq)
  ## else, name based on minutes in sampling period
  if epoch <= 1:
    freq = int(1.0/epoch)
    return '%dHzEpoch' % freq
  else:
    mins = int(epoch/60)
    return '%dMinEpoch' % mins

def getAllVariables(progXmlDir):
  vars = towerVariables()
  for file in os.listdir(progXmlDir):
    if isProgXML(file):
      progXML = xml.dom.minidom.parse(progXmlDir + '/' + file)
      vars = addVariables (progXML, vars)
  return vars
  
def test():
  vars = getAllVariables('sampleProgXml')
  obsTypes, obsLimits = getObservations('observations.xml')
  
  
  ## make for today only
  now = time.localtime()
  startYear = now[0]
  startDOY = now[7]
  makeEmptyNetcdf(fileName(startYear, startDOY), vars, obsTypes, obsLimits)
 
      
    
      
  
if __name__ == '__main__':
  test()
