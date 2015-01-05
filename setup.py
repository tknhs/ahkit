#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='ahkit',
    description='Active History of Research for K.I.T.',
    version='0.1',
    author='tknhs',
    packages=find_packages(),
    install_requires=['docopt', 'GitPython', 'PyYAML', 'selenium'],
    entry_points={
        'console_scripts': 'ahkit = ahkit.ahkit:main'
    },
    zip_safe=False,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Education',
        'Natural Language :: Japanese',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
