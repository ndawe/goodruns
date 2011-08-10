#!/usr/bin/env python

import pkginfo
from distutils.core import setup
from glob import glob

setup(name='goodruns',
      version=pkginfo.__RELEASE__,
      author='Noel Dawe',
      author_email='noel.dawe@cern.ch',
      url='https://github.com/ndawe/goodruns',
      description='ATLAS "good runs list" utilities',
      long_description='An implementation of an ATLAS "good runs list" reader/writer in Python, and collection of useful command-line tools.',
      download_url='https://github.com/ndawe/goodruns/tarball/v1.0',
      license='GPLv3',
      py_modules=['goodruns'],
      requires=['yaml', 'lxml'],
      scripts=glob('scripts/*')
     )
