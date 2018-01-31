# A simple routine to guess DSP experiment name and version from experiment path
# Follows download.cgi but simplified
# C F Enell 20161116, 20171113

class DSPname:

    
    #Experiment dictionary:
    #DSP name : [list of possible exp path names]
    # note: taken from schedule download.cgi function
    # 20171113: added a few non-Guisdap names found in 2015 archive

    def __init__(self):
        exps={'arc':['arc'],
              'arc1':['arc1','arc_slice'],
              'dlayer':['dlayer'],
              'arcd':['arcd','arc_dlayer'],
              'beata':['beata'],
              'bella':['bella'], 
              'cp0e':['cp0e','cp-0-e'],
              'cp0g':['cp0g','cp-0-g'], 
              'cp0h':['cp0h','cp-0-h'], 
              'cp1c':['cp1c','cp-1-c'],
              'cp1f':['cp1f','cp-1-f'], 
              'CP1H':['CP1H','cp1h','CP-1-H','cp-1-h'],
              'cp1j':['cp1j','cp-1-j'],
              'cp1k':['cp1k','cp-1-k'],
              'cp1l':['cp1l','cp-1-l'],
              'cp1m':['cp1m','cp-1-m'],
              'cp2c':['cp2c','cp-2-c'],
              'cp3c':['cp3c','cp-3-c'],
              'cp4b':['cp4b','cp-4-b'],
              'cp7h':['cp7h','cp-7-h'],
              'folke':['folke'],
              'hilde':['hilde'],
              'gup0':['gup0'],
              'gup1':['gup1'],
              'gup3c':['gup3c'],
              'ipy':['ipy'],
              'lace':['lace'],
              'leo':['leo_bpark','leo'],
              'lt1':['lt1'],
              'lt2':['lt2'],
              'manda':['manda'],
              'mete':['mete'],
              'pia':['pia'],
              'steffe':['steffe','steffel'],
              'tau0':['tau0'],
              'tau1':['tau1'],
              'tau1a':['tau1a'],
              'tau2':['tau2'],
              'tau2pl':['tau2pl','tau2_pl'],
              'tau3':['tau3'],
              'tau7':['tau7'],
              'tau8':['tau8'],
              'taro':['taro'],
              'uhf1g2':['uhf1g2','sp-vi-uhf1-g2']}
    
        # Map path name to DSP exp name by finding possible exp name part
        # 20171113:  default empty string.
        def dsp(self,filename):

            dsp=''

            for exp in self.exps:
                for expname in exps[exp]:
                    if filename.count(expname)>0:
                        dsp=exp

            if not dsp.isalnum():
                print("Warning: No experiment name found in name string " + filename)
                print("Metadata string will be empty")

            return dsp
            
        # Find experiment version from exp name part
        # 20171113:  Search by regexp, default to '1.0' if not in name
        def ver(self,filename):    

            import re

            try:
                vs=re.search('\w*_(?P<ver>\d\.\d*)\w*_\w*',filename)
                ver=vs.group('ver')
            except:
                ver='1.0'
                print("Warning: No experiment version found in name string " + filename)
                print("Assuming " + ver)
        
            return ver


            
    

    

          
