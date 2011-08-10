#!/usr/bin/env python

import pkginfo
from distutils.core import setup
from glob import glob

setup(name='goodruns',
      version=pkginfo.__RELEASE__,
      description='ATLAS "good runs list" utilities',
      author='Noel Dawe',
      author_email='noel.dawe@cern.ch',
      url='https://github.com/ndawe/goodruns',
      description='An implementation of an ATLAS "good runs list" reader/writer in Python, and collection of useful command-line tools.',
      long_description='',
      download_url='',
      license='GPLv3',
      py_modules=['goodruns'],
      requires=['yaml', 'lxml'],
      scripts=glob('scripts/*')
     )
