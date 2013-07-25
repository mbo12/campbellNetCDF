#### from a csv file of the form "obsName,varName,obsUnits,minValue,maxValue"
# create an observations.xml file
import xmlutils
csvFormat = ['obsName','varName','varUnits','minValue','maxValue']

def main():
  obsXml = xmlutils.createNewXML('observations')

  obs = 'obs.csv'
  with open(obs,'rU') as f:
    observations = f.readlines()

    for o in observations:
      obsNode = xmlutils.addNode(obsXml,'root',"observation")
      fields = o.rstrip().split(',')
      for i in range(len(csvFormat)):
        if not (len(fields[i])==0 ) and len(fields[i].split())>0:
            xmlutils.addTextElement(obsXml,obsNode,csvFormat[i],fields[i])

  xmlout = open('observations.xml','w')
  print >> xmlout, xmlutils.cleanupXML(obsXml)
  
if __name__ == '__main__':
  main()
