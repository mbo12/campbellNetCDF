import xml.dom.minidom
import re
"""Module with a couple of xml helper functions"""
DTD_FILE = 'ecohydrology.dtd'

### add an element with tagName and text content "value" as a child of 
### parentElement in doc  
def addTextElement (doc,parentElement,tagName,value):
  node = doc.createElement(tagName)
  node.appendChild(doc.createTextNode(str(value)))
  if parentElement == 'root': 
    parentElement = doc.documentElement
  parentElement.appendChild(node)
  
def addNode(doc,parentElement,tagName):
  node = doc.createElement(tagName)
  if parentElement == 'root': 
    parentElement = doc.documentElement
  parentElement.appendChild(node)
  return node

# reformats xml so that it is easier to read if opened in texteditor    
def cleanupXML (doc):
  xml = doc.toprettyxml()
  ## get rid of extra whitespaces/newlines in text tag
  text_re = re.compile('>\s+([^<>\s].*?)\s*</', re.DOTALL)    
  xml = text_re.sub('>\g<1></', xml)
  
  ## case where value is empty (only extra whitespaces)
  text_re = re.compile('(<[^/<>]*?)>\s*</', re.DOTALL)
  prettyXml = text_re.sub('\g<1>></', xml)
  space_re = re.compile('>\n\s*\n(\s*)<')
  prettyXml = space_re.sub('>\n\g<1><', prettyXml)

  ## soft indent
  tab_re = re.compile('\t')
  prettyXml = tab_re.sub('  ', prettyXml)
  return prettyXml
  
  
def getText (node,tag):
  textNode = node.getElementsByTagName(tag)
  try: return textNode[0].childNodes[0].data
  except: return None
  
# new xml doc of program type following ecohydrology.dtd  
def createNewProgramXML ():
  imp = xml.dom.minidom.DOMImplementation()
  doctype = imp.createDocumentType ('program', '', DTD_FILE)
  doc = imp.createDocument(None, 'program', doctype)
  return doc  
  
def createNewXML(root):
  imp = xml.dom.minidom.DOMImplementation()
  doctype = imp.createDocumentType (root, '', DTD_FILE)
  doc = imp.createDocument(None, root, doctype)
  return doc
def addTextNodeToRoot (doc,nodeName,nodeValue):
  newNode = doc.createElement(nodeName)
  (doc.documentElement).appendChild(newNode)
  nodeTxt = doc.createTextNode(nodeValue)
  newNode.appendChild(nodeTxt)
  return doc
