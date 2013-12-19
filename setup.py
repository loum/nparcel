import os
import glob
import fnmatch
import shutil
from distutils.core import setup

VERSION = '0.23'


def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)


def find_data_files(srcdir, *wildcards, **kw):
    """Get a list of all files under the *srcdir* matching *wildcards*,
    returned in a format to be used for install_data.

    """

    def walk_helper(arg, dirname, files):
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if (fnmatch.fnmatch(filename, wc_name) and
                    not os.path.isdir(filename)):
                    if kw.get('version') is None:
                        names.append(filename)
                    else:
                        versioned_file = '%s.%s' % (filename,
                                                    kw.get('version'))
                        shutil.copyfile(filename, versioned_file)
                        names.append('%s.%s' % (filename,
                                                kw.get('version')))

        if names:
            if kw.get('target_dir') is None:
                lst.append(('', names))
            else:
                lst.append((kw.get('target_dir'), names))

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

files = find_data_files('doc/build/',
                        '*.html',
                        '*.png',
                        '*.js',
                        '*.css',
                        recursive=True,
                        target_dir='doc/build')
template_files = find_data_files('nparcel/templates/', '*.t')
nparcel_conf_file = find_data_files('nparcel/conf/',
                                    '*.conf',
                                    version=VERSION)
log_conf_file = find_data_files('nparcel/utils/conf/',
                                '*.conf',
                                version=VERSION)

setup(name='python-nparcel',
      version=VERSION,
      description='Nparcel B2C Replicator',
      author='Lou Markovski',
      author_email='lou.markovski@tollgroup.com',
      url='https://nparcel.tollgroup.com',
      scripts=['nparcel/bin/nploaderd',
               'nparcel/bin/npexporterd',
               'nparcel/bin/npreminderd',
               'nparcel/bin/npftp',
               'nparcel/bin/npmts',
               'nparcel/bin/npinit',
               'nparcel/bin/nppostcode',
               'nparcel/bin/npondeliveryd',
               'nparcel/bin/npcommsd',
               'nparcel/bin/npmapperd',
               'nparcel/bin/npfilterd',
               'nparcel/bin/npreporter'],
      packages=['nparcel',
                'nparcel.table',
                'nparcel.utils',
                'nparcel.openpyxl',
                'nparcel.openpyxl.shared',
                'nparcel.openpyxl.shared.compat',
                'nparcel.openpyxl.reader',
                'nparcel.openpyxl.writer'],
      package_dir={'nparcel': 'nparcel'},
      package_data={'nparcel': ['conf/*.conf.[0-9]*.[0-9]*',
                                'templates/*.t',
                                'utils/conf/*.conf.[0-9]*.[0-9]*',
                                'conf/init.conf']},
      data_files=files)
