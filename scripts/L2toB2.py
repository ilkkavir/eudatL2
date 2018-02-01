#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""
L2toB2.py

Produce B2SHARE entries and HDF5 files for Level 2 data and metadata.
Processes specified time interval creating one HDF file per hourly subdirectory.

Usage: L2toB2.py <start year> <start month> <start day> <end year> <end month> <end day>

(C) Carl-Fredrik Enell EISCAT HQ  2018
carl-fredrik.enell@eiscat.se
"""

### Required standard libraries
import sys, os
import calendar, datetime
from configparser import SafeConfigParser
from multiprocessing import Pool, cpu_count

### Local modules
from EISCATL2catalog import catalogquery
from B2entry import b2entry

### Main program

if __name__=='__main__':

    config=SafeConfigParser(inline_comment_prefixes={'#'})    
    config.read('/usr/local/etc/eudatL2.conf')

    baseURI=config.get("Main","baseURI")
    verbose=config.getboolean("Main","verbose")
        
    ## parse arguments
    if len(sys.argv) != 7:
        print("Usage: %s year1 month1 day1 year2 day2 month2" % (sys.argv[0]))
        exit(1)

    byear=int(sys.argv[1])
    bmonth=int(sys.argv[2])
    bday=int(sys.argv[3])

    eyear=int(sys.argv[4])
    emonth=int(sys.argv[5])
    eday=int(sys.argv[6])
                
    outpath=config.get("Main","outDir")
                
    assert 1981 <= byear <= 2015, "Years from 2016 have different info locations, not handled yet"
    assert 1 <= bmonth <= 12, "Invalid start month"
    assert 1 <= bday <= calendar.monthrange(byear,bmonth)[1], "Invalid day in start month"
        
    assert byear <= eyear <= 2015, "Years from 2016 have different info locations, not handled yet"
    assert 1 <= emonth <= 12, "Invalid end month"
    assert 1 <= eday <= calendar.monthrange(eyear,emonth)[1], "Invalid day in end month"
        
    t1=datetime.datetime(byear,bmonth,bday, 0,0,0)
    t2=datetime.datetime(eyear,emonth,eday, 23,59,59)
    assert t2 > t1, "End time must be after start time"
                
    if not os.path.exists(outpath):
        if verbose:
            print("Creating output directory %s" % (outpath))

        os.makedirs(outpath)
    else:
        print("Warning: %s exists. Any existing HDF files may be overwritten." % (outpath))

    ## List experiments in db
    qlist=[]
        
    with catalogquery.CatalogQuery(config) as DBq:
        eids = DBq.get_ids(t1,t2)

        # Get the exp locations
        for eid in eids:
                        
            meta=DBq.get_meta(eid['experiment_id'])
            assert (len(meta)==1),  "Ambiguous: more than one entry for this expid"

            meta=meta[0]    
            elocs=DBq.get_locs(eid['resource_id'])                        
                        
            # Get all info resIDs                        
            for eloc in elocs:
                # identify correct info time (TODO: 2016 and later)
                locate_time=datetime.datetime.strptime(eloc['location'].split('/')[-1],'%Y%m%d_%H')
                midnight1=locate_time.strftime('%Y-%m-%d 00:00:00')
                midnight2=locate_time.strftime('%Y-%m-%d 23:59:59')

                # find info directory
                count=0
                iid=DBq.get_info_ids(eid['experiment_id'],midnight1,midnight2)

                while len(iid)<1 and count < 5:
                    print("searching backward")
                    midnight1=datetime.datetime.strptime(midnight1,'%Y-%m-%d %H:%M:%S')-datetime.timedelta(1)
                    midnight1=midnight1.strftime('%Y-%m-%d %H:%M:%S')
                    midnight2=datetime.datetime.strptime(midnight2,'%Y-%m-%d %H:%M:%S')-datetime.timedelta(1)
                    midnight2=midnight2.strftime('%Y-%m-%d %H:%M:%S')
                    iid=DBq.get_info_ids(eid['experiment_id'],midnight1,midnight2)
                    count=count+1                                                

                    try:
                        iid=iid[0]
                        iloc=DBq.get_locs(iid['resource_id'])
                        iloc=iloc[0]
                    except:
                        iloc={'location': ''}
                                        
                    resource=eid['account'] or meta['country']
                    # remove eiscat-raid://host/ for  actual data path
                    location=eloc['location'].replace(baseURI,'')
                    
                    # Build array of arrays
                    # [[ResID, ExpName, Antenna, Resource, DBStartTime, DBStopTime, Location, InfoPath, outPath],...]
                    qlist.append([eid['resource_id'],meta['experiment_name'],meta['antenna'],resource,eid['start'],eid['end'],location,iloc['location'],outpath])


    if len(qlist)==0:
        print("No data found in interval " + t1.strftime('%Y-%m-%dT%H:%M:%S') + " -- " + t2.strftime('%Y-%m-%dT%H:%M:%S') + ". Nothing to do.")
        sys.exit(0)
                                
    if verbose:
        print("%d hourly directories in queue" % (len(qlist)))
                                
    ## Process the queue list                
    # Limit no of parallel processes
    maxproc=config.getint('Main','maxproc')
    nproc=min(maxproc,cpu_count())
    if nproc > 1:
        nproc=min(len(qlist),nproc)
    else:
        nproc=1

    print("Starting %d processes" % nproc)
    # Start processing all entries in qlist
    p=Pool(nproc)
    p.map(b2entry.B2Entry(), qlist)

    # Terminate all processes (necessary?) 
    p.close()
    p.join()
        
    if verbose:
        print("%s ready" % (sys.argv[0]))
### End of program
