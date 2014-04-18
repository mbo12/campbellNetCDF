import xml.dom.minidom
import re
import loggernetfile
import xmlutils
import time, datetime
import netCDF4
import createNetcdfs

PROGXML = 'sampleProgXml/'
MAXBUFFER = 180000
BYTES_TO_READ = 10485760
ROOTNAME = 'MpalaTower' # root name for netcdf file<

def getProgName(program):
  return xmlutils.getText(program, 'progName')

class DataFile():
  def __init__(self, file_name, program_name, table_name):
    self.header_lines_read = 0
    self.has_header = loggernetfile.hasAHeader(file_name)
    self.file_name = file_name
    self.program_name = program_name
    self.table_name = table_name
    self.start_date = loggernetfile.getFirstDate(file_name)
    self.end_date = self.__get_end_date()
    self.__get_info_from_xml()
    self.dataset = None
    self.__get_needed_ncid()
    self.__init_empty_buffer()

  def __get_info_from_xml(self):
    program_xml = getXML(self.program_name)
    for table_node in program_xml.getElementsByTagName('table'):
      if xmlutils.getText(table_node, 'tableName') == self.table_name:
        self.table_xml = table_node
        self.epoch = float(xmlutils.getText(table_node, 'outputInterval'))
        self.group_name = createNetcdfs.groupName(self.epoch)
        self.var_ids = varNames(table_node, program_xml)
  
  def __init_empty_buffer(self):
    self.data = dict()
    for var in self.table_xml.getElementsByTagName('variable'):
      if xmlutils.getText(var, 'flag'): continue
      col = int(xmlutils.getText(var, 'tableColumn')) + 1
      self.data[col] = []

  def process(self):
    self.records_saved = 0
    with open(self.file_name, 'rU') as f:
      lines = f.readlines(BYTES_TO_READ)
      while lines:
        for line in lines:
          if self.has_header and self.header_lines_read < 4:
            self.header_lines_read += 1
            continue
          self.__process_line(line)
        lines = f.readlines(BYTES_TO_READ)
      self.__dump_data()
      self.dataset.close()

  def __process_line(self, line):
    fields = line.split(',')
    
    #if fields[0] >= startDate and fields[0] >= lastDate:
    #  lastDate = fields[0]
    if fields[0][1:-1] >= self.end_date:
      self.__dump_data()
      self.start_date = fields[0][1:-1]
      self.end_date = self.__get_end_date()
      self.__get_needed_ncid()

    elif self.records_saved >= MAXBUFFER:
      self.__dump_data()
      self.start_date = fields[0][1:-1]
    for col in self.data:
      if fields[col] == '"NAN"': fields[col] = float('nan')
      elif fields[col] == '"INF"': fields[col] = float('nan')
      elif fields[col] == '"-INF"': fields[col] = float('nan')
      else: fields[col] = float(fields[col])
      self.data[col].append(fields[col])
      self.records_saved += 1

  def __dump_data(self):
    for col in self.data:
      if not self.data[col]:continue
      var_id = getVarID(self.ncid, col, self.var_ids)
      ### FIX TODO
      start = self.__get_ind_from_date()
      end = start + len(self.data[col])
      if self.var_ids[col] == "Year": continue
      var_id[start:end] = self.data[col]
      self.data[col] = []
    self.records_saved = 0

  def __get_ind_from_date(self):
    hour = int(self.start_date[11:13])
    minute = int(self.start_date[14:16])
    second = int(self.start_date[17:19])
    if len(self.start_date) > 19:
      second += float("0." + self.start_date[20:])
    total_seconds = 60 * (hour * 60 + minute) + second
    return int(total_seconds / self.epoch)

  def __get_needed_ncid(self):
    if self.dataset:
      self.dataset.close()
    self.dataset = netCDF4.Dataset(self.__get_file_name(), 'r+')
    self.ncid = self.dataset.groups[self.group_name]

  def __get_file_name(self):
    year = int(self.start_date[0:4])
    month = int(self.start_date[5:7])
    day = int(self.start_date[8:10])
    doy = datetime.datetime(year, month, day).timetuple().tm_yday
    return ROOTNAME + '_%d_%03d.nc' % (year, doy)
  
  def __get_end_date(self):
    year = int(self.start_date[0:4])
    month = int(self.start_date[5:7])
    day = int(self.start_date[8:10])
    end = datetime.datetime(year, month, day)
    end += datetime.timedelta(days=1)
    return "%d-%02d-%02d 00:00:00" % (end.year, end.month, end.day)
    
def getXML(programName):
  return xml.dom.minidom.parse(PROGXML + programName + '.xml')
 
 
def get_date_range(year, doy):
  today = time.localtime()
  endDate = '"%4d-%02d-%02d 00:00:00"' %((today[0]),today[1] ,today[2])
  yesterday = (datetime.datetime.fromtimestamp((time.time()-60*60*24)).timetuple())
  startDate = '"%4d-%02d-%02d 00:00:00"' %((yesterday[0]),yesterday[1] ,yesterday[2])
  return (startDate,endDate)
 

def varNames(table, progXml):
  names = dict()
  for var in table.getElementsByTagName('variable'):
      if xmlutils.getText(var, 'flag'):continue
      name = xmlutils.getText(var, 'varName')
      col = int(xmlutils.getText(var, 'tableColumn'))+1
      #if re.search('batt', name, flags=re.IGNORECASE):
      #  print getProgName(progXml)
      #  name = name+'_'+getProgName(progXml)
      names[col] = name
  return names
  
def getVarID(ncid, col, varIDs):
  return ncid.variables[varIDs[col]]
    
  
