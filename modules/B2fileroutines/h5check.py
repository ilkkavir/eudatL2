### Helper subroutine for dataset creation and insertion
### into open HDF5 file

def insert_data(hf,hKey,indata,dataType,verbose):

    # check scalar or vector
    try:
        nCols=len(indata)
    except:
        nCols=1
                
    # check if dataset exists
    if not hf.__contains__(hKey):
        if verbose:
            print("Creating dataset " + hKey)
            
        try:
            if nCols > 1:
                # create compressed vector dataset
                
                try:
                    if dataType:
                        hf.create_dataset(hKey, data=indata, dtype=dataType, compression='gzip', shuffle=True)
                    else:        
                        hf.create_dataset(hKey, data=indata, compression='gzip', shuffle=True)
                except:
                    if dataType:
                        hf.create_dataset(hKey, data=indata[:,0], dtype=dataType, compression='gzip', shuffle=True)
                    else:    
                        hf.create_dataset(hKey, data=indata[:,0], compression='gzip', shuffle=True)

            else:
                # scalar dataset
                hf.create_dataset(hKey, data=indata)
        except:
            # String data 
            hf[hKey]=u'%s' % indata
                
    else:
        print("something is weird: dataset already existing in HDF output")
        raise IOError
