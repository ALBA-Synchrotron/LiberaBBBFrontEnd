#!/usr/bin/env python

from setuptools import setup

# The version is updated automatically with bumpversion
# Do not update manually
__version = '1.0.3'


setup(
    name='LiberaBBBFrontEnd',
    version=__version,
    package_dir={'LiberaBBBFrontEnd': 'src'},
    packages=['LiberaBBBFrontEnd'],
    include_package_data=True,  # include files in MANIFEST
    author='Jairo Moldes',
    author_email='jmoldes@cells.es',
    description='Tango device servers for controlling Libera BBB FE',
    license='GPLv3+',
    platforms=['src', 'noarch'],
    url='https://github.com/ALBA-Synchrotron/LiberaBBBFrontEnd',
    requires=['tango (>=7.1.1)'],
    entry_points={
        'console_scripts': [
            'LiberaBBBFrontEnd = LiberaBBBFrontEnd.LiberaBBBFrontEnd:main',
        ],
    },
)
