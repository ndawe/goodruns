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
      long_description=open('README.rst').read(),
      download_url='https://github.com/ndawe/goodruns/tarball/v1.0',
      license='GPLv3',
      py_modules=['goodruns', 'pkginfo'],
      requires=['yaml', 'lxml'],
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
      ]
    )
