import re
import sys
import xml.dom.minidom
from xmlutils import addTextElement, getText
""" This module contains the class definition for Table (see below) as well as
some private helper methods for the Table functions.  
Table also incorporates Variables and Variable objects.
Basically, the creation of a Table parses crbasic text."""


commandRE = re.compile(r'^\s*(\w*)\((.*?)\)\s*$')
basenameRE = re.compile(r'^(.*?)((_\d+)|(\(\d+\)))?$')
abbrev = {'Average':'_Avg','Totalize':'_Tot','Sample':'','StdDev':'_Std','Minimum':'_Min','Maximum':'_Max','WindVector':'_Wvc'}


### reverse lookup value "find" in a dictionary "ref"
def _revdic(ref,find):    
  for k,v in ref.iteritems():
    if v == find: 
      return k

def _getBasename(varName):
  name = basenameRE.match(varName)
  return name.group(1)

### pull out an instrument associated with var from a file that follows dtd
### for instrumentlibrary.dtd    
def _getInstrument(var):
  varNode = var.parentNode
  insNode = varNode.parentNode.parentNode
  insName = insNode.getElementsByTagName("insName")
  return insName[0].childNodes[0].data  

  

class Variables:
  def __init__(self):
    self.variables = []
    
  def getVar(self,name):
     if name in self.variables:
       return self.variables[self.variables.index(name)]
     else:
       for j in self.variables:
         if j.alias == name:
           return j
           
  def addVar(self,name):
    new = Variable(name)
    self.variables.append(new)

     
class Variable:
  def __init__(self,name):
    self.name = name
    self.alias = ''
    self.fieldname = ''
    self.units = ''
  
  def __cmp__(self,other):
    return self.name==other
    




      
         
class Table:
  """ The Table class is used to represent a CampbellSci/CRBasic Table. 
  Tables have a name, an output interval, and variables that
  it is recording.  
  A Table is initialized with text from the logger program.
  Operations defined on a Table include parsing that text and processing that
  text so that it can be written out to our program xmls."""
  
  ### initialize the table based on table text from program as well as
  ### the aliases, constants, and units defined for the program
  def __init__(self,tableText,aliases,constants,units):
      self.tableText = tableText
      self.name = self.__getTableName(tableText)
      self.aliases = aliases
      self.constants = constants
      self.units = units
      self.commands = self.__allCommands(tableText)
      self.interval = self.__getOutputPeriod(tableText)
      
      self.outputInstructions = self.__getOutputInstructions(tableText)
      self.colPosition = 0
      
  ### add outputInterval and tableName to the programxml      
  def addTableInfo (self,doc,tableNode):
    addTextElement(doc,tableNode,'outputInterval',self.interval)
    addTextElement(doc,tableNode,'tableName',self.name)  
    
    
  ### see if there are units assigned for this variable
  def lookupUnits (self,variable):
    if variable in self.units:
      return (self.units[variable])
    ### units can also defined by the var's alias
    elif variable in self.aliases and self.aliases[variable] in self.units:
      return (self.units[self.aliases[variable]])
    else:
      ### sometimes units are defined for whole array--check for this  
      array = re.search('(.*?)\(?(\d*)\)',variable)
      if array and array.group(1) in self.units:
        return self.units[array.group(1)]
      else:
        return ''
  

  ## if instrument is in our library, return observationType info  
  def lookupInstrument(self,variable,insLib):
    baseName = _getBasename(variable)
    variables = insLib.getElementsByTagName('varName')
    for j in variables:
      name = j.childNodes[0].data
      if name==baseName:
        ins=_getInstrument(j)
        obs=getText(j.parentNode,'obsName')
        return (ins,obs)
    return (None,None)
    
  
  ### go through the output instructions for this table and write the variable
  ### info to the program xml          
  def processOutputInstructions (self,doc,variables,insLib):
    for meas in self.outputInstructions:
      # repeated measurment on an array variable
      for i in range(meas[2]):
        self.colPosition += 1 
        if i > 0:
          meas[1] = self.__incrementArrayIndex (meas[1])
        
        varNode = doc.createElement("variable")
       
        # add metadata for this variable
        
        addTextElement(doc,varNode,'varName',self.__varNameToWriteOut((i+1),meas,abbrev[meas[0]]))
        addTextElement(doc,varNode,'origName',self.__origName((i+1),meas,abbrev[meas[0]]))
        ins,obs = self.lookupInstrument(meas[1],insLib)
        if ins:
          addTextElement(doc,varNode,'insName',ins)
          addTextElement(doc,varNode,'obsName',obs)  
        addTextElement(doc,varNode,'tableColumn',self.colPosition)
        addTextElement(doc,varNode,'varUnits',self.lookupUnits(meas[1]))
        addTextElement(doc,varNode,'varType',meas[0])
        
        variables.appendChild(varNode)

  def __allCommands (self,text):
    commands = [(self.__getCommand(j) for j in text.splitlines())]

  # what command/operation does this measurement instruction use (eg average)
  def __getCommand (self,line):
    command = commandRE.match(line)
    if command:
      params = command.group(2).split(',')
      return command.group(1),params
            
  ### variable name that is being written out (fieldnames or aliases)
  def __varNameToWriteOut (self,rep,instruction,abbrev):
      if len(instruction) > 3 + (rep-1):
        ### store fieldname
        return instruction[3][rep-1]
      elif  instruction[1] in self.aliases:
        return self.aliases[instruction[1]]+abbrev
      else: ### no fieldnames or aliases defined
        array = re.match('^(.*?)(\(\d+\))$',instruction[1])
        if array:
          return array.group(1)+abbrev+array.group(2)
        else:
          return instruction[1]+abbrev
  
  def __origName (self,rep,instruction,abbrev):
     ### does it have an alias or fieldname?
     if instruction[1] + abbrev != self.__varNameToWriteOut(rep,instruction,abbrev):
       return instruction[1]
     ### is it an alias or field name
     aliasToOrig = _revdic(self.aliases,instruction[1])
     if aliasToOrig:  ##handle array caseX
        array = re.match('^(.*?)(\(\d+\))$',aliasToOrig)
        if array:
          return array.group(1)+abbrev+array.group(2)
        else:
          return aliasToOrig #+abbrev
     return instruction[1]


    
     
  ### adjust index based on rep of output instruction        
  def __incrementArrayIndex (self,variable):
    array = re.search('(.*?)\s*\(?(\d*)\)',variable)
    variable = array.group(1) + '(' + str(int(array.group(2))+1) + ')'
    return variable
  
  ### parse measurement instruction to get parameters  
  def __getInstructionParameters(self,instructionName,parameterNumber):
    line = re.search(instructionName+r'\s*\((.*?)\)',self.tableText)
    if not line and instructionName =='DataInterval':
      return '1'
    params = line.group(1).split(',')
    paramNeeded = re.search(r'^\s*(.*?)\s*$',params[parameterNumber-1])
    return paramNeeded.group(1)
    
  def __getTableName (self,table):
    return self.__getInstructionParameters('DataTable',1)

  ### output instructions
  def __getOutputInstructions (self,table):
    outputInstructions = 'Average|StdDev|Totalize|Minimum|Maximum|Sample'
    output =[]

    lines = table.splitlines()
   
    for i in range(len(lines)):
      instruction = re.search(r'^\s*('+outputInstructions+')\s*\((.*)\)',lines[i])

      if instruction:
        parameters = instruction.group(2).split(',')
        for j in range(len(parameters)):
          nowhitespace=re.match('^\s*(.*?)\s*$',parameters[j])
          parameters[j]=nowhitespace.group(1)
        ### make sure reps is a number. if it is a constant, replace
        isInt = re.search('^\s*\d*\s*$',parameters[0])
        if not isInt:
          parameters[0] = self.constants[parameters[0]]
          
        ### we use a numeric comparison later, so convert from string  
        parameters[0] = int(parameters[0])
        
        ### if first rep (of multiple) isn't array, use reverse lookup in aliases
        ### we need to work in array form to understand what next variable will be
        if parameters[0] > 1 :
          array = re.search('(.*?)\(?(\d*)\)',parameters[1])
          if not array:
            parameters[1] = _revdic(self.aliases,parameters[1])
            array = re.search('(.*?)\(?(\d*)\)',parameters[1])
            if not array:
              raise Exception('variable with multiple reps not in array format')
              
              
        ### if we're writing fieldnames, return them too
        if i+1 != len(lines): 
          fieldnames = re.search(r'^\s*FieldNames\s*\("(.*)"\)',lines[i+1])
          if fieldnames:
            names = fieldnames.group(1).split(',')
            output.append([instruction.group(1),parameters[1],parameters[0],names])
            continue
        
        output.append([instruction.group(1),parameters[1],parameters[0]])

    return output

  ### find frequency of this table
  def __getOutputPeriod (self,table):
    ## returns the output period of a table in seconds
    interval = self.__getInstructionParameters('DataInterval',2)
    if interval:
      time = re.search(r'^\d*$',interval)
      if not time:
        ### we don't have support for expressions (ie CONST + CONST)
        time = re.search(r'^\s*(.*?)\s*$',interval)
        interval = self.constants[time.group(1)]
      interval = float(interval)
      units = self.__getInstructionParameters('DataInterval',3)
      if units == "Min":
        interval = interval * 60
      elif  units == "mSec":
        interval = interval / 1000.0
      return interval
    
