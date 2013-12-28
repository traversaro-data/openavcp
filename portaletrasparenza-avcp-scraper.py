#!/usr/bin/env python3


'''Scraper for  http://portaletrasparenza.avcp.it website. Download 
   all the data available and publish it to a github repository.
   Usage (the tool should be used inside the data/ directory of the repository): 
      portaletrasparenza-avcp-scraper.py download (to download the data)
      portaletrasparenza-avcp-scraper.py indent (to indent in a clean way the data)
      portaletrasparenza-avcp-scraper.py push (to push the data on github)
   You can also combine the operation, so that they can be executed in series, for example:
      portaletrasparenza-avcp-scraper.py download indent push
   Downloads the data, indent it and it pushes it on a github 
'''


#Web interface documentation:
#First argument: search key (name or fiscal code) (-100 for wildcard)
#second: year
#third: month (-100 apprently for all the months for website generated queries)
#forth: 0 for closed tenders, 1 for acrive ones (-100 for wildcard)
#URL = portaletrasparenza.avcp.it/Microstrategy/asp/export_xml.aspx?valuepromptanswers=^^^

import os
import sys
import requests
import getopt
import subprocess
import xml.dom.minidom
import codecs
import datetime


#Year to scrape
years_to_download = range(2011,2015)
months_in_a_year = range(1,13)

github_username = "username"
github_password = "password"

#from http://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
def download_file(url,filename=""):
    if( filename == "" ):
        local_filename = url.split('/')[-1]
    else:
        local_filename = filename
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename

def xml_filename(year,month):
    return "avcp_contracts_"+str(year)+"_"+'%02d' % month+".xml";

def push_data_to_github():
    for year in years_to_download:
        for month in months_in_a_year:
            subprocess.call(["git","add",xml_filename(year,month)])
    
    commit_msg = "Data updated at " + datetime.datetime.now().isoformat()
    subprocess.call(["git","commit","-m",commit_msg])
    subprocess.call(["git","push"])
 
    return
  
def indent_data():
    for year in years_to_download:
        for month in months_in_a_year:
            filename = xml_filename(year,month)
            print("Indenting " + filename);
            xml_dom = xml.dom.minidom.parse(filename) 
            pretty_xml_as_string = xml_dom.toprettyxml(indent="  ")
            f = codecs.open(filename,'w','utf-8')
            f.write(pretty_xml_as_string)
            f.close()

def download_data():
    '''Download all the data available in AVCP http://portaletrasparenza.avcp.it
       in raw xml data. The data is splitted at each month to avoid reaching
       the maximum query limit'''
    print("Downloading data")

    
    for year in years_to_download:
        for month in months_in_a_year:
            url = "http://portaletrasparenza.avcp.it/Microstrategy/asp/export_xml.aspx?valuepromptanswers=-100^"+str(year)+"^"+str(month)+"^-100"
            print("Downloading file " + xml_filename(year,month));
            download_file(url,xml_filename(year,month))
    
def process(arg):
    if( arg == "download" ):
        download_data()
    if( arg == "indent" ):
        indent_data()
    if( arg == "push" ):
        push_data_to_github()
   
def main():
    '''Main method for the scraper'''
        # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error:
        print("for help use --help")
        sys.exit(2)
        
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        if o == "--github_user":
            print("Using github user " + a)
        if o == "--github_password":
            print("Using github password " + a)
            
    # process arguments
    for arg in args:
        process(arg) # process() is defined elsewhere
        
    

if __name__ == "__main__":
    main()
