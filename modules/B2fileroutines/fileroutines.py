class Fileroutines:

    """ 
    Routines to read and write EISCAT data files
    to hourly HDF5 files.
    """
    
    def __init__(self,verbose):
        # Global definition
        self.verbose=verbose
        
    def readMatBz2(self,matfile):
        ## Input function for bzipped matlab files.
        ## Input: Path to matlab file
        ## Reads .mat file, either normal or compressed with bz2
        ## Return: data
        ## Relies on file extension. TODO: check file type properly. Now handled by try/except blocks.
        from bz2 import BZ2File 
        from scipy.io import loadmat
        
        if matfile.endswith('mat.bz2'):
            # EISCAT archive standard: bzipped mat files
            try:
                mf=BZ2File(matfile,'r')
            except:
                raise IOError('Could not open file %s for reading' % matfile)

        elif matfile.endswith('mat'):
            # Assume this is a normal mat file
            try:
                mf=open(matfile,'r')
            except:
                raise IOError('Could not open file %s for reading' % matfile)                         
        else:
            raise IOError('Not a .mat or .mat.bz2 file: %s' % matfile) 

        # Load the content of mat file
        try:
            dd=loadmat(mf,mat_dtype=False,squeeze_me=False,chars_as_strings=True,matlab_compatible=False)                
        except:
            raise IOError('Could not read Matlab data from %s' % matfile)

        mf.close()        

        # Return content of mat file
        return dd


    def B2file(self,args):
        ### The hourly HDF5 file writer
        # Version string: bump if changed HDF5 format
        efVersion='2018013102'

        # Standard libraries
        import os
        import datetime
        from h5py import File as h5file
        import tarfile
        from numpy import array, exp2, log2, ceil
        from configparser import SafeConfigParser

        # Local libraries
        from B2fileroutines import h5check, dspname, pointdir 

        # Creation at current time
        cTime=datetime.datetime.today().isoformat()
    
        #Unpack input
        resID,expName,Antenna,Resources,dbStartTime,dbStopTime,dataDir,infoDir,outputDir=args

        ## EISCAT data definitions. TODO move to config file.
        # Matlab file variables to HDF Data/ structure
        dataMap={'d_data' : 'Data/%s/L2', 'd_raw' : 'Data/%s/L1', 'd_parbl' : 'Data/%s/Parameters' }
        # Data types
        dtMap={'d_data' : 'double', 'd_raw' : 'i2'} 
    
        # Matlab d_parbl entries to HDF Metadata structure
        metaKey=['d_parbl']
        endTimeIdx=slice(0,6)
        intTimeIdx=6
        antIdx=40 # VHF: 3

        # UHF parbl mapping
        metaMap={7 : 'MetaData/%s/Power', 8 : 'MetaData/%s/Elevation', 9 : 'MetaData/%s/Azimuth' }
    
        # VHF parbl mapping
        vhfAnt=3
        VmetaMap={7 : 'MetaData/%s/Power', 9 : 'MetaData/%s/Azimuth'}
        velIdx=slice(64,68)

        ## Gather info if infoDir is not empty
        ubsize=0
        if infoDir:

            # Tar info dir to temporary file
            config=SafeConfigParser(inline_comment_prefixes={'#'})
            config.read('/usr/local/etc/eudat.conf')
            baseURI=config.get("Main","baseURI")
            tmpdir=config.get("Main","tempDir")
    
            idir=infoDir.replace(baseURI,'') # local path
            tarpath=os.path.join(tmpdir,str(resID)+'-info.tar.bz2')
    
            if self.verbose:
                print('Creating info tar data %s' % tarpath)

            with tarfile.open(tarpath,'w|bz2') as tfile:
                tfile.add(idir)
                
            # Put tarred data in memory for userblock
            with open(tarpath,'rb') as tfile:
                ub=tfile.read()
    
            if self.verbose:
                print('Removing temporary file %s' % tarpath)

            # Delete temporary tar file
            os.remove(tarpath)
    
            # User block size must be a power of 2 >= 512
            ubsize=max(512,int(exp2(ceil(log2(len(ub))))))
        
        ## Open HDF5 file for writing
        hourDirName=os.path.basename(dataDir.strip('/'))
        dayDirName=hourDirName.split('_')[0]
        outFileBase=os.path.join(dayDirName,str(resID) + '-' + expName + '_' + Antenna + '-' + hourDirName + '.hdf5') # URL part of filename
        outFile=os.path.join(outputDir,outFileBase) # Full filesystem path
        if self.verbose:
            print("Writing to " + outFile)

        if not(os.path.exists(os.path.dirname(outFile))):
            os.makedirs(os.path.dirname(outFile))
            
        try:
            hf=h5file(outFile,'w',driver='sec2',userblock_size=ubsize)

        except:
            raise IOError('Could not create file %s' % outFile)
        
        ## Sort out mat.bz2 files and count number of files = number of data records for HDF5 file
        inFiles=sorted(os.listdir(dataDir))
        inFiles=[f for f in inFiles if (f.endswith('.mat.bz2') or f.endswith('.mat'))]

        ## Main loop over mat files
        recordNo=0.0

        # keep start and stop times from records
        fileStartTime=datetime.datetime.utcnow()+datetime.timedelta(1) #always in future
        fileStopTime=datetime.datetime(1970,1,1,0,0,0) #Min UNIX time
    
        ## Track azimuth/elevation
        az=[]
        el=[]
            
        for inFile in inFiles:
            if self.verbose:
                print("Mat file no %d" % recordNo)
            timestamp=os.path.basename(inFile).split('.')[0]
            inpData=self.readMatBz2(os.path.join(dataDir,inFile))

            # Gather data records
            for key in inpData.keys():

                if key in metaKey:
                    # Handle metadata records: (V)metaMap (parameter no : HDF name)
                    indata=inpData[key]

                    # First create start and stop time strings                
                    dumpEndTime=datetime.datetime(*[int(t) for t in indata[0][endTimeIdx]])
                    fileStopTime=max(fileStopTime, dumpEndTime)
                
                    intTime=indata[0][intTimeIdx]                
                    dumpStartTime=dumpEndTime-datetime.timedelta(seconds=intTime)
                    fileStartTime=min(dumpStartTime, fileStartTime)
                
                    h5check.insert_data(hf,'MetaData/%s/startTime' % (timestamp), dumpStartTime.isoformat(),False,self.verbose)
                    h5check.insert_data(hf,'MetaData/%s/endTime' % (timestamp), dumpEndTime.isoformat(),False,self.verbose)

                    # Map other parbl metadata
                    isvhf=indata[0][antIdx]==vhfAnt
                    if  isvhf:
                        #VHF
                        # Elevation vector separately
                        vel=indata[0][velIdx]
                        h5check.insert_data(hf,'MetaData/%s/Elevation' % (timestamp),vel,False,self.verbose)

                        #Save to az/el grid
                        for elev in vel:
                            el.append(elev)
                        
                        theMap=VmetaMap
                    else:
                        #UHF, ESR
                        theMap=metaMap
                    
                    # The rest of the metadata
                    for hInd in theMap.keys():
                        hKey=theMap[hInd] % (timestamp)
                        val=indata[0][hInd]
                        # create / add dataset
                        h5check.insert_data(hf,hKey,val,False,self.verbose)

                        # keep track of min and max aximuth
                        if hKey.find('Azimuth')>0:
                            az.append(val)
                            if isvhf:
                                # append 3 more azimuths to match len(vel)
                                for _ in range(0,3):
                                    az.append(val)
                                
                        # keep track of min and max elevation (except VHF)
                        if hKey.find('Elevation')>0 and not isvhf:
                            el.append(val)

                # Data records; use dataMap (matlab var name : HDF name)
                try:
                    hKey=dataMap[key]
                except:
                    hKey=[]

                dataType=False
                
                if hKey:
                    if hKey.find('%')>0:
                        hKey = hKey % (timestamp)
                    
                    # format input to array or string
                    indata=inpData[key]            
                    h5check.insert_data(hf,hKey,indata,dataType,self.verbose)

                
            # Next
            recordNo=recordNo+1
        
        ## End of loop

        # Creation and version stamp
        h5check.insert_data(hf,'MetaData/CreationTime',cTime,False,self.verbose)
        h5check.insert_data(hf,'MetaData/EudatfileVersion',efVersion,False,self.verbose)
    
    
        # Add the SQL metadata 
        h5check.insert_data(hf,'MetaData/ID',resID,False,self.verbose)
        h5check.insert_data(hf,'MetaData/ExperimentName',expName,False,self.verbose)
        h5check.insert_data(hf,'MetaData/DSPexp',dspname.DSPname(expName).dsp(),False,self.verbose)
        h5check.insert_data(hf,'MetaData/DSPver',dspname.DSPname(expName).ver(),False,self.verbose)
        h5check.insert_data(hf,'MetaData/Antenna',Antenna,False,self.verbose)
        h5check.insert_data(hf,'MetaData/Resources',Resources,False,self.verbose)
        h5check.insert_data(hf,'MetaData/StartTime',fileStartTime,False,self.verbose)
        h5check.insert_data(hf,'MetaData/StopTime',fileStopTime,False,self.verbose)

        if dbStartTime != fileStartTime:
            if self.verbose:
                print('Warning: DB timestamp does not agree')
            h5check.insert_data(hf,'MetaData/DBStartTime',dbStartTime,False,self.verbose)

        if dbStopTime != fileStopTime:
            if self.verbose:
                print('Warning: DB timestamp does not agree')
            h5check.insert_data(hf,'MetaData/DBStopTime',dbStopTime,False,self.verbose)

        h5check.insert_data(hf,'MetaData/InfoDir',infoDir,False,self.verbose)
    
        # Azimuth- elevation hull
        azel=pointdir.AzEl(az,el).boundary()
        h5check.insert_data(hf,'MetaData/AzElLimits',azel,False,self.verbose)
    
        # Close outfile
        if self.verbose:
            print("Closed output file " + outFile)
        hf.close()

        # Put the raw user block in the outfile
        # (nb: file must be closed and reopened in raw mode to manipulate user block)
        if ubsize:
            with open(outFile,'r+b') as hf:
                # mode r+ allows to overwrite partially
                hf.seek(0)
                hf.write(ub)
    
            if self.verbose:
                print('Added info dir to user block of %s' % outFile)

        # return URL part of filename
        return outFileBase
### Done
