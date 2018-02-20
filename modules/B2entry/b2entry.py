class B2Entry:

    """ 
    L2 data (matlab file) conversion
    to HDF5 files with B2SHARE entries.
    
    This is a callable class (for compatibility with multiprocessing)
    which is in essence a wrapper for B2fileroutines.fileroutines 
    and B2SHARE API routines.
    """    
    
    def __init__(self):

        from configparser import SafeConfigParser
        self.config=SafeConfigParser(inline_comment_prefixes={'#'})
        self.config.read('/usr/local/etc/eudatL2.conf')
        self.verbose=self.config.getboolean('Main','verbose')
        
    def __call__(self,args):

        ## Hourly HDF5 file writer
        # debugging B2share routines: use an existing HDF file
        #-- from B2fileroutines import fileroutines
        #-- outFile=fileroutines.Fileroutines(self.verbose).B2file(args)
        outFile='/data/eudat/2014-02-04/238426-beata_zenith_2.0v_CP_vhf-20140402_07.hdf5'
        
        ## Create a B2SHARE record for this file?
        if self.config.getboolean('B2','b2share_entry'):
            
            from B2SHAREClient import B2SHAREClient,EISCATmetadata
            from json import loads
            ## Set up one client instance 
            client=B2SHAREClient.B2SHAREClient(community_id=self.config.get('B2','community'), url=self.config.get('B2','b2share_url'),token=self.config.get('B2','token') )

            ## Create a draft
            # Format JSON metadata
            (basic_json, json_patch) = EISCATmetadata.MetaDataPatch(args, self.config.get('B2','local_base_url') + outFile, self.config.get('B2','community'), self.config.get('B2','community_specific'))

            # Create the B2SHARE entry
            draft_json=client.create_draft(basic_json)            
            
            # Insert community metadata
            print(draft_json['id'])
            client.update_draft(draft_json['id'], json_patch)

            # Insert file
            if 'file' in draft_json.keys:
                client.upload_file(draft_json['files'], outFile)
