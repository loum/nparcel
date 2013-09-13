import os
import glob
import fnmatch
from distutils.core import setup


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
                    names.append(filename)
        if names:
            lst.append((dirname, names))

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
                        recursive=True)


setup(name='python-nparcel',
      version='0.10',
      description='Nparcel B2C Replicator',
      author='Lou Markovski',
      author_email='lou.markovski@tollgroup.com',
      url='https://nparcel.tollgroup.com',
      scripts=['nparcel/bin/nploaderd',
               'nparcel/bin/npexporterd',
               'nparcel/bin/npftp'],
      packages=['nparcel', 'nparcel.table', 'nparcel.utils'],
      data_files=files)
