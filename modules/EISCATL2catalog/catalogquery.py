class CatalogQuery:

        """ 
        Queries to  EISCAT Level 2 file catalogue system (MySQL DB: disk_archive)
        """        

        import MySQLdb

        def __init__(self, config):

                # Common definition/s
                # Set base uri of wanted locations (remove to obtain physical storage path)
                self.base_loc=config.get("Main","BaseURI")

                # Make connection to DB.
                self.db=self.MySQLdb.connect(host=config.get("DB","dbHost"),user=config.get("DB","dbUser"),passwd=config.get("DB","dbPass"),db=config.get("DB","db"))
                self.cur=self.db.cursor(self.MySQLdb.cursors.DictCursor)

        ## Constructor / destructor for usage with 'with' 
        def __enter__(self):
                return self

        def __exit__(self, exc_type, exc_value, traceback):
                # Close connection to DB
                self.cur.close()
                self.db.close()

        ## DB query abstractions
        def get_ids(self,t1, t2):

                """ List all resource and experiment IDs between t1 and t2 """

                q="SELECT resource_id,experiment_id,start,end,account FROM resource WHERE type LIKE \'data\' AND start > \'%s\' AND end < \'%s\';" % (t1,t2,)
                self.cur.execute(q)

                return self.cur.fetchall()

        def get_locs(self,resid):

                """ Get the location/s of resource id resid matching base_loc """

                q="SELECT location FROM storage WHERE resource_id=%d AND location LIKE \'%%%s%%\'" % (resid,self.base_loc,)
                self.cur.execute(q)

                return self.cur.fetchall()                

        def get_meta(self,expid):

                """ Get required information about the experimnet """

                q = "SELECT experiment_name, country, antenna FROM experiments WHERE experiment_id=%d" % (expid,)
                self.cur.execute(q)

                return self.cur.fetchall()
        
        def get_info_ids(self, expid, t1, t2):

                """ List resource ids of info dirs of experiment expid dated on correct day """

                q="SELECT resource_id FROM resource WHERE experiment_id=%d AND start>=\'%s\' AND start <=\'%s\'  AND type LIKE \'info\'" % (expid, t1, t2)
                self.cur.execute(q)

                return self.cur.fetchall()
