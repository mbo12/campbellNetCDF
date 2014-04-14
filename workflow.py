#
import argparse
import calendar
import createNetcdfs

def days_in_year(year):
    if calendar.isleap(year):
        return 366
    else:
        return 365

def files_to_make(start_date, end_date):
    start_year = int(start_date[:4])
    end_year = int(end_date[:4])
    start_day = int(start_date[5:8])
    end_day = int(end_date[5:8])
    for y in range(start_year, end_year + 1):
        if y == start_year:
            first_day = start_day
        else:
            first_day = 1
        if y == end_year:
            last_day = end_day
        else:
            last_day = days_in_year(y)
            
        for d in range(first_day, last_day + 1):
            file_name = createNetcdfs.fileName(y, d)
            yield file_name

def main():
    parser = argparse.ArgumentParser(description='Run netcdf workflow')
    parser.add_argument('--start_date', help='start netcdf date in format YYYY_DOY, eg 2014_001', required=True)
    parser.add_argument('--end_date', help='end netcdf date in format YYYY_DOY, eg 2014_365', required=True)
    parser.add_argument('--program_xml_dir', help='location of program xml files', required=True)
    parser.add_argument('--obs_xml_file', help='path of observation.xml file', required=True)

    args = parser.parse_args()

    vars = createNetcdfs.getAllVariables(args.program_xml_dir)
    obsTypes, obsLimits = createNetcdfs.getObservations(args.obs_xml_file)
    for file_name in files_to_make(args.start_date, args.end_date):
        createNetcdfs.makeEmptyNetcdf(file_name, vars, obsTypes, obsLimits)


if __name__ == '__main__':
    main()
