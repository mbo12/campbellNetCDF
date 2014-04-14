#### 
# create an observations.xml file
# usage: python makeObsXML.py INPUT_FILE OUTPUT_FILE
# input: from a csv file of the form "obsName,varName,obsUnits,minValue,maxValue"
# output: xml file

import xmlutils
import sys
csvFormat = ['obsName','varName','varUnits','minValue','maxValue']

def main():
  obsXml = xmlutils.createNewXML('observations')

  obs = sys.argv[1]
  with open(obs,'rU') as f:
    observations = f.readlines()

    for o in observations:
      obsNode = xmlutils.addNode(obsXml,'root',"observation")
      fields = o.rstrip().split(',')
      for i in range(len(csvFormat)):
        if not (len(fields[i])==0 ) and len(fields[i].split())>0:
            xmlutils.addTextElement(obsXml,obsNode,csvFormat[i],fields[i])

  xmlout = open(sys.argv[2],'w')
  print >> xmlout, xmlutils.cleanupXML(obsXml)
  
if __name__ == '__main__':
  main()
