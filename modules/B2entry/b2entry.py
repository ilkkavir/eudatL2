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
        self.config.read('/usr/local/etc/eudatL2.conf')
        self.verbose=self.config.getboolean('Main','verbose')
        
    def __call__(self,args):

        # Hourly HDF5 file writer
        from B2fileroutines import fileroutines
        fileroutines.Fileroutines(self.verbose).B2file(args)

        # Create a B2SHARE record for this file?
        if self.config.getboolean('B2','b2share_entry'):
            
            print("Creating B2SHARE record")
            from B2SHAREClient import B2SHAREClient,EISCATmetadata
            
            # Set up one client instance
            # Could read the parameters from the config file where it is opened in B2SHAREClient.py,
            # but this allows multiple instances (Training and production?)
            self.community_id=self.config.get('B2','community')
            self.community_specific_id=self.config.get('B2','community_specific')

            b2c=B2SHAREClient.B2SHAREClient(community_id=self.community_id, url=self.config.get('B2','b2share_url'),token=self.config.get('B2','token') )

            # Create a draft
            draft_id=args[0] # Resource ID
            draft=client.get_draft(draft_id)

            # Insert metadata
            json_patch=EISCATmetadata.MetaDataPatch(args,self.community_specific_id)
            client.update_draft(draft, json_patch)
            
        
        
    
