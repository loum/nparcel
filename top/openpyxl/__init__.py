# file openpyxl/__init__.py

# Copyright (c) 2010-2011 openpyxl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# @license: http://www.opensource.org/licenses/mit-license.php
# @author: see AUTHORS file

"""Imports for the openpyxl package."""

# package imports
from nparcel.openpyxl import cell
from nparcel.openpyxl import namedrange
from nparcel.openpyxl import style
from nparcel.openpyxl import workbook
from nparcel.openpyxl import worksheet
from nparcel.openpyxl import reader
from nparcel.openpyxl import shared
from nparcel.openpyxl import writer

# shortcuts
from nparcel.openpyxl.workbook import Workbook
from nparcel.openpyxl.reader.excel import load_workbook

# constants

__major__ = 1  # for major interface/format changes
__minor__ = 5  # for minor interface/format changes
__release__ = 8  # for tweaks, bug-fixes, or development

__version__ = '%d.%d.%d' % (__major__, __minor__, __release__)

__author__ = 'Eric Gazoni'
__license__ = 'MIT/Expat'
__author_email__ = 'eric.gazoni@gmail.com'
__maintainer_email__ = 'openpyxl-users@googlegroups.com'
__url__ = 'http://bitbucket.org/ericgazoni/openpyxl/wiki/Home'
__downloadUrl__ = "http://bitbucket.org/ericgazoni/openpyxl/downloads"

__all__ = ('reader', 'shared', 'writer',)
