import re
""" A few simple functions to extract information from campbell sci
raw data files... assuming a toa5 file format"""

def getLine(filename, n):
  # return the nth line of filename
  with open(filename, 'rU') as filePtr:
    for j in range(n):
      line = filePtr.readline()
    return line.rstrip()
  
def getFields(filename, n):
  ## get values of csv filename for line n
  line = getLine(filename, n)
  return line.split(',')
  
def isAValidDataFile(filename):
  if filename[0] == "." :
    return False
  ext = re.search('(\.\w*)((\.\d*)?\.backup)?$', filename)
  if not ext: return False
  if (ext.group(1) == ".dat"):
    return (not re.search('zip', filename))

def hasAHeader(file):
  line = getLine(file, 1)
  return line[0:6] == '"TOA5"'


def getLoggerName(file):
  fields = getFields(file, 1)
  #chomp off quotes
  return fields[2][1:-1] + "_" + fields[3][1:-1]  
    
def getProgName(file):
  fields = getFields(file, 1)
  match = re.search('CPU:(.*)"$', fields[5])
  return match.group(1)
  
def getFirstDate(file):
  if hasAHeader(file):
    fields = getFields(file, 5)
  else:
    fields = getFields(file, 1)
  return fields[0][1:-1]
  
def getVariablesFromHeader(file):
  return getLine(file, 2)

def getTableName(file):
  fields = getFields(file, 1)
  return fields[7][1:-1]
