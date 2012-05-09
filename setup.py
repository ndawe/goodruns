#!/usr/bin/env python

import os
import sys
from glob import glob


requires = ['python>=2.5', 'argparse']

execfile('goodruns/info.py')

if USE_LXML:
    requires.append('lxml')
else:
    requires.append('PyXML')

if USE_YAML:
    requires.append('PyYAML')

kw = {}
if os.getenv('GOODRUNS_NO_DISTRIBUTE') in ('1', 'true'):
    from distutils.core import setup
    packages = ['goodruns']
    if sys.version_info >= (2, 5):
        kw['requires'] = requires
else:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    packages = find_packages()
    kw['install_requires'] = requires

open('version.txt', 'w').write(__version__)

if os.getenv('GOODRUNS_AFS_INSTALL') in ('1', 'true'):
    prefix = '/afs/cern.ch/atlas/software/tools/goodruns/'
else:
    prefix = 'etc/goodruns'

if 'install' in sys.argv:
    print __doc__

setup(name='goodruns',
      version=__version__,
      author='Noel Dawe',
      author_email='noel.dawe@cern.ch',
      description='ATLAS "good run list" utilities',
      long_description=open('README.rst').read(),
      url=__url__,
      download_url=__download_url__,
      license='GPLv3',
      packages=packages,
      scripts=glob('scripts/*'),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Utilities",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)"
      ],
      **kw
    )
os.unlink('version.txt')
