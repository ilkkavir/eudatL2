from distutils.core import setup

setup(name = "eudatL2", 
      version="2018020801", 
      author="Carl-Fredrik Enell",
      author_email="carl-fredrik.enell@eiscat.se",
      url="http://www.eiscat.se/raw/fredrik/",
      package_dir = {'': 'modules'},
      packages = ['EISCATL2catalog','B2entry','B2fileroutines','B2SHAREClient'],
      scripts = ['scripts/L2toB2.py'],
      data_files=[
          ('/usr/local/etc/',['config/eudat.conf'])
    ]
  )
