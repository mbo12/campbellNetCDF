import bisect
import loggernetfile
import os, sys

class Deployments():
    def __init__(self):
        self.loggers = {}
    
    def check_file(self, file_name):
        if loggernetfile.hasAHeader(file_name):
            start_date = loggernetfile.getFirstDate(file_name)
            logger_name = loggernetfile.getLoggerName(file_name)
            prog_name = loggernetfile.getProgName(file_name)
            self.add_deployment(logger_name, prog_name, start_date)

    def add_deployment(self, logger_name, prog_name, start_date):
        if logger_name not in self.loggers:
            self.loggers[logger_name] = [(start_date, prog_name)]
            return

        ind = bisect.bisect(self.loggers[logger_name], (start_date, prog_name))
        max_ind = len(self.loggers[logger_name])
        if ind > 0 and self.loggers[logger_name][ind - 1][1] == prog_name:
            return
        if ind < max_ind and self.loggers[logger_name][ind][1] == prog_name:
            self.loggers[logger_name][ind] = (start_date, prog_name)
        else:
            bisect.insort(self.loggers[logger_name], (start_date, prog_name))
            

    def print_all(self):
        for logger in self.loggers.keys():
            print logger
            for date, version in self.loggers[logger]:
                print date, version

    def find_program_running(self, logger_name, campbell_date):
        ind = 0
        while ind < len(self.loggers[logger_name]) - 1 and self.loggers[logger_name][ind + 1][0] <= campbell_date:
            ind += 1
        return self.loggers[logger_name][ind][1]

def recursiveFileList(dir):
  fileList = []
  for root, subFolders, files in os.walk(dir):
      for file in files:
          fileList.append(os.path.join(root,file))
  return fileList


def gen_files(dir):
  for root, subFolders, files in os.walk(dir):
      for file in files:
          yield os.path.join(root,file)


def main():
    tower = Deployments()
    loc = sys.argv[0]
    for file in genFiles(loc):
        if(loggernetfile.isAValidDataFile(os.path.basename(file))):
            tower.check_file(file)
    tower.print_all()

if __name__ == '__main__':
  main()
