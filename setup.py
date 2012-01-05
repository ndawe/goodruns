#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup
from glob import glob

execfile('goodruns/info.py')

setup(name='goodruns',
      version=__VERSION__,
      author='Noel Dawe',
      author_email='noel.dawe@cern.ch',
      description='ATLAS "good run list" utilities',
      long_description=open('README.rst').read(),
      url=__URL__,
      download_url=__DOWNLOAD_URL__,
      license='GPLv3',
      packages=['goodruns'],
      scripts=glob('scripts/*'),
      install_requires = ['python>=2.5', 'argparse'],
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
