from distutils.core import setup

setup(name='python-nparcel',
      version='0.1',
      description='Nparcel B2C Replicator',
      author='Lou Markovski',
      author_email='lou.markovski@tollgroup.com',
      url='https://nparcel.tollgroup.com',
      scripts=['nparcel/bin/nparceld'],
      packages=['nparcel', 'nparcel.table', 'nparcel.utils'],)
