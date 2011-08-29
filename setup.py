#!/usr/bin/env python

from distutils.core import setup
from glob import glob

execfile('info.py')

setup(name='goodruns',
      version=__RELEASE__,
      author='Noel Dawe',
      author_email='noel.dawe@cern.ch',
      url=__URL__,
      description='ATLAS "good run list" utilities',
      long_description=open('README.rst').read(),
      download_url="%sgoodruns-%s.tar.gz" % (__URL__, __VERSION__),
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
