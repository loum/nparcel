import os
import glob
import fnmatch
import shutil
from distutils.core import setup

VERSION = '0.38'


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
template_files = find_data_files('top/templates/', '*.t')
top_conf_file = find_data_files('top/conf/',
                                '*.conf',
                                 version=VERSION)
log_conf_file = find_data_files('top/utils/conf/',
                                '*.conf',
                                version=VERSION)

setup(name='python-top',
      version=VERSION,
      description='Toll Outlet Portal Middleware',
      author='Lou Markovski',
      author_email='lou.markovski@tollgroup.com',
      url='https://nparcel.tollgroup.com',
      scripts=['top/bin/toploaderd',
               'top/bin/topexporterd',
               'top/bin/topreminderd',
               'top/bin/topftp',
               'top/bin/topinit',
               'top/bin/toppostcode',
               'top/bin/topondeliveryd',
               'top/bin/topcommsd',
               'top/bin/topmapperd',
               'top/bin/topfilterd',
               'top/bin/topreporter',
               'top/bin/tophealth',
               'top/bin/toppod',
               'top/bin/topadpd',
               'top/bin/toppodmigrate',
               'top/bin/toppoderd',
               'top/bin/topctrl'],
      packages=['top',
                'top.table',
                'top.report',
                'top.utils',
                'top.b2cconfig',
                'top.openpyxl',
                'top.openpyxl.shared',
                'top.openpyxl.shared.compat',
                'top.openpyxl.reader',
                'top.openpyxl.writer'],
      package_dir={'top': 'top'},
      package_data={'top': ['conf/*.conf.[0-9]*.[0-9]*',
                            'templates/*.t',
                            'utils/conf/*.conf.[0-9]*.[0-9]*',
                            'conf/init.conf']},
      data_files=files)
