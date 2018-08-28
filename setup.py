#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='docassemble.jcc.ability-to-pay',
      version='0.0.0',
      description=('JCC Ability to Pay'),
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      author='Ari Chivukula',
      author_email='ari.c@berkeley.edu',
      license='MIT',
      url='http://www.courts.ca.gov/',
      packages=find_packages(),
      zip_safe = False,
     )
