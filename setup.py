#!/usr/bin/env python

# Place current directory at the front of PYTHONPATH
import sys
sys.path.insert(0,'.')

from goodruns import pkginfo
from distutils.core import setup
from glob import glob

setup(name='goodruns',
      version=pkginfo.__RELEASE__,
      description='ATLAS good runs lists utilities',
      author='Noel Dawe',
      author_email='noel.dawe@cern.ch',
      url='https://github.com/noeldawe/goodruns',
      packages=['goodruns'],
      requires=['rootpy', 'yaml', 'lxml'],
      scripts=glob('scripts/*')
     )

