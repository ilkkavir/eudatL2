from distutils.core import setup

setup(name = "eudatL2", 
      version="2018013101", 
      author="Carl-Fredrik Enell",
      author_email="carl-fredrik.enell@eiscat.se",
      url="http://www.eiscat.se/raw/fredrik/",
      package_dir = {'': 'modules'},
      packages = ['B2fileroutines','EISCATL2catalog'],
      scripts = ['scripts/L2toB2.py'],
      data_files=[
          ('/usr/local/etc/',['config/eudatL2.conf'])
    ]
  )
