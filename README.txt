More walkthroughs here: http://mbo12.github.io/campbellNetCDF/

This code sample represents an effort to extract information from CRBASIC datalogger programs (made by Campbell Scientific).  CRBASIC is a language that runs on microprocessors commonly used in the environmental sciences. 

A CRBASIC program structure is:
Declare variables and constants
Declare units for observations
Define data tables to be saved to storage on uC
Write program control and measurement loop

The data file resulting from the crbasic program has 4 headers lines (with those variable names and units), but this is not a sufficient form of metadata documentation in the scientific research context. Here, I parse the crbasic program text and extract that metadata and put it in an xml format. In this way, I can easily combine with other relevant metadata that is found from outside the crbasic program (eg site lat/lon, sensor specs and serial numbers, user calibration events, etc) which I've also set up an xml format for. In this example, some metadata from instrumentlibrary.xml is included in the output (making it more information dense than the crbasic csv header).

The objective is to increase documentation quality so to better allow collaborating with the data. Automation of the documentation is chosen whenever possible.

A sample workflow to put it all together is in workflow.py:
usage: python workflow.py  --start_date START_DATE --end_date END_DATE
                   --program_xml_dir PROGRAM_XML_DIR --obs_xml_file
                   OBS_XML_FILE --data_dir DATA_DIR
The script will make empty netcdfs from START_DATE to END_DATE based on schema from the supplied xml files. Then, all the loggernet files in DATA_DIR will be added to the proper netcdfs. (The campbell headers are using the line up the data files with the proper program xml. There is some hackery to account for program files without a header since that occurs when campbell makes backup files).
