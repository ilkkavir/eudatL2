class B2Entry:

    """ 
    The entry point to L2 data conversion
    to HDF5 files with B2SHARE entries.
    
    This is a callable class (for compatibility with multiprocessing)
    which is in essence a wrapper for fileroutines and B2SHARE API routines.
    """    
    
    def __init__(self):

        from configparser import SafeConfigParser
        self.config=SafeConfigParser(inline_comment_prefixes={'#'})
        self.config.read('/usr/local/etc/L2write.conf')
        self.verbose=self.config.getboolean('Main','verbose')
        
    def __call__(self,args):
        # Hourly HDF5 file writer
        from B2fileroutines import fileroutines
        fileroutines.Fileroutines(self.verbose).B2file(args)

        if self.config.getboolean('B2','b2share_entry'):
            # Create a B2SHARE record for this file
            print("Creating B2SHARE record")
            
        
        
        
        
        
    
