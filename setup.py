#!/usr/bin/env python3

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

with open("requirements.txt", "r") as f:
    REQUIRED_PACKAGES = f.read().splitlines()

setup(name='minos',
      version='0.0.1',
      description='Microsimulation package for investigation pathways to mental health',
      long_description=readme(),
      url='https://github.com/Leeds-MRG/Minos',
      author='Benjamin Isaac Wilson, Camila Rangel Smith, Kasra Hosseini, Luke Archer, Robert Clay',
      author_email='l.archer@leeds.ac.uk, gyrc@leeds.ac.uk',
      license='MIT',
      packages=['minos'],
      zip_safe=False,
      install_requires=REQUIRED_PACKAGES,
      test_suite='nose.collector',
      tests_require=['nose'],
      )