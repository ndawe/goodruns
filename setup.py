#!/usr/bin/env python

import pkginfo
from distutils.core import setup
from glob import glob

setup(name='goodruns',
      version=pkginfo.__RELEASE__,
      description='ATLAS "good runs list" utilities',
      author='Noel Dawe',
      author_email='noel.dawe@cern.ch',
      url='https://github.com/noeldawe/goodruns',
      py_modules=['goodruns'],
      requires=['yaml', 'lxml'],
      scripts=glob('scripts/*')
     )
