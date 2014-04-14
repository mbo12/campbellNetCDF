from xml.dom.minidom import Document, DOMImplementation, parse
import xml.dom.minidom
import sys, os
import re
from Table import Table
import Program
import xmlutils 
    
## usage: python makeProgXML.py CRBASRIC_PROG_FILENAME

def main ():
  
  prog = sys.argv[1]
  ## open program to parse (read whole program into memory, it's small enough)
  with open(prog,'r') as f:
    towerProgram = Program.removeCommentedText(f.read())
    
  ### parse instrumentlibrary for additional metadata
  insLib = parse('instrumentlibrary.xml')  
    
  ## parse program to get aliases, constants, and units
  aliases = Program.getAliases(towerProgram)  
  constants = Program.getConstants(towerProgram)
  units = Program.getUnits(towerProgram)

  ## start and initialize new xml for this program
  doc = xmlutils.createNewProgramXML()
  xmlutils.addTextNodeToRoot(doc,"progName",prog)
  tablesNode = xmlutils.addNode(doc,'root','tables')
 
  ### put datatable info in the progxml
  tables = Program.getTables(towerProgram)
  for text in tables:
    ### use text and program info to construct Table object
    table = Table(text,aliases,constants,units)

    ### add table info (name and interval) to xml
    tableNode = doc.createElement("table")
    table.addTableInfo(doc,tableNode)

    ### process output instructions and store variable info
    ### to the progxml
    variablesNode = xmlutils.addNode(doc,tableNode,'variables')
    table.processOutputInstructions(doc,variablesNode,insLib)
   
    tablesNode.appendChild(tableNode)


  #do some cleaning up of xml (so it's easy for humans to view in texteditor)
  progxml = xmlutils.cleanupXML(doc)
  ### save progxml
  xmlout = open(prog + '.xml','w')
  print >>xmlout, progxml
 
  
if __name__ == '__main__':
  main()
