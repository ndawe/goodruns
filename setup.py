#!/usr/bin/env python

import sys

if sys.version_info < (2, 5):
    raise RuntimeError("goodruns supports python 2.5 and above")

from glob import glob
import os
# Prevent setup from trying to create hard links
# which are not allowed on AFS between directories.
# This is a hack to force copying.
try:
    del os.link
except AttributeError:
    pass

local_path = os.path.dirname(os.path.abspath(__file__))
# setup.py can be called from outside the rootpy directory
os.chdir(local_path)
sys.path.insert(0, local_path)

from setuptools import setup, find_packages

execfile('goodruns/info.py')

requires = []
if USE_LXML:
    requires.append('lxml')

if 'install' in sys.argv:
    print __doc__

setup(
    name='goodruns',
    version=__version__,
    author='Noel Dawe',
    author_email='noel.dawe@cern.ch',
    description='ATLAS Good Run List (GRL) reader and utilities',
    long_description=open('README.rst').read(),
    url=__url__,
    download_url=__download_url__,
    license='GPLv3',
    packages=find_packages(),
    scripts=glob('scripts/*'),
    install_requires=requires,
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Utilities',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Development Status :: 5 - Production/Stable',
    ])
