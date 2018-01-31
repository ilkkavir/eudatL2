class B2Entry:

    """ 
    The entry point to L2 data conversion
    to HDF5 files with B2SHARE entries.
    
    This is a callable class (for compatibility with multiprocessing)
    which is in essence a wrapper for fileroutines and B2SHARE API routines.
    """
    
    from B2fileroutines import fileroutines
    
    def __init__(self,verbose):
        # Global definition of verbosity
        self.verbose=verbose
        
    def __call__(self,args):
        # Hourly HDF5 file writer

        self.fileroutines.Fileroutines(self.verbose).B2file(args)


    
