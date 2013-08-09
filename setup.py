from distutils.core import setup

setup(name='python-nparcel',
      version='0.4',
      description='Nparcel B2C Replicator',
      author='Lou Markovski',
      author_email='lou.markovski@tollgroup.com',
      url='https://nparcel.tollgroup.com',
      scripts=['nparcel/bin/nploaderd',
               'nparcel/bin/npexporterd'],
      packages=['nparcel', 'nparcel.table', 'nparcel.utils'],)
