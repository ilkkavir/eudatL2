#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""
L2toB2simple.py

Produce B2SHARE entries and HDF5 files for Level 2 data and metadata.
Processes specified time interval creating one HDF file per hourly subdirectory.
This is a simplified version that does not read any information from the EISCAT DB

Usage: L2toB2.py <expname> <antenna> <datadir> <outputdir>

(C) Carl-Fredrik Enell EISCAT HQ  2018
carl-fredrik.enell@eiscat.se
"""

### Required standard libraries
import sys, os
import calendar, datetime

### Local modules
from B2fileroutines import fileroutines

### Main program

if __name__=='__main__':

    verbose=True
        
    ## parse arguments
    if len(sys.argv) != 5:
        print("Usage: %s expname antenna datadir outputdir" % (sys.argv[0]))
        exit(1)
        
    expname=sys.argv[1]
    antenna=sys.argv[2]
    datapath=sys.argv[3]
    outpath=sys.argv[4]
                
##    assert 1981 <= byear <= 2015, "Years from 2016 have different info locations, not handled yet"
##    assert 1 <= bmonth <= 12, "Invalid start month"
##    assert 1 <= bday <= calendar.monthrange(byear,bmonth)[1], "Invalid day in start month"
        
##    assert byear <= eyear <= 2015, "Years from 2016 have different info locations, not handled yet"
##    assert 1 <= emonth <= 12, "Invalid end month"
##    assert 1 <= eday <= calendar.monthrange(eyear,emonth)[1], "Invalid day in end month"
        
    t1=datetime.datetime(1980,1,1, 0,0,0)
    t2=datetime.datetime(2100,12,31, 23,59,59)
##    assert t2 > t1, "End time must be after start time"
                
    if not os.path.exists(outpath):
        if verbose:
            print("Creating output directory %s" % (outpath))

        os.makedirs(outpath)
    else:
        print("Warning: %s exists. Any existing HDF files may be overwritten." % (outpath))


    print("Starting mat to hdf5 conversion")
    fr = fileroutines.Fileroutines(verbose)
    for root, ddirs, dfiles in os.walk(datapath):
        for ddir in ddirs:
            # Start processing all entries in qlist
            datadir = os.path.join(root,ddir)
            fr.B2file(['EISCAT',expname,antenna,'',t1,t2,datadir,False,outpath])


        
    if verbose:
        print("%s ready" % (sys.argv[0]))
### End of program
