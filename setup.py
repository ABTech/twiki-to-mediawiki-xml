#!/usr/bin/env python
"""
setup.py: Package setup file.

Created by Perry Naseck on 2022-05-23.
This file is part of the https://github.com/ABTech/twiki-to-mediawiki-xml

Copyright (C) 2022-present  AB Tech, Carnegie Mellon University
Copyright (C) 2022          Perry Naseck (git@perrynaseck.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import pathlib
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name="twiki-to-mediawiki-xml",
    description="TWiki to MediaWiki XML conversion tool",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPLv3',
    author="AB Tech",
    author_email="abtech@andrew.cmu.edu",
    python_requires='>=3.8, <4',
    packages=find_packages(),
    platforms=["any"],
    url="https://github.com/ABTech/twiki-to-mediawiki-xml",
    project_urls={
        'Bug Reports': 'https://github.com/ABTech/twiki-to-mediawiki-xml/issues',
        'Source': 'https://github.com/ABTech/twiki-to-mediawiki-xml',
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Framework :: Robot Framework',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent',
        'Topic :: Communications',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ],
    keywords='twiki mediawiki xml wiki migrate migration convert tool utility python perl python3 wikitext',
    entry_points = {
        'console_scripts': [
            'twiki-to-mediawiki-xml=twiki_to_mediawiki_xml.scripts.twiki_to_mediawiki_xml:main'
        ],
    },
    install_requires=[
        # Pypi is missing wheels and sources
        'editrcs @ git+https://github.com/ben-cohen/editrcs.git@8307af79ba6abe5f76313cd747fc53439d99959b#egg=editrcs',
        'lxml>=4,<5'
    ],
    extras_require={
        'dev': [
            'bandit>=1,<2',
            'flake8>=4,<5',
            'flake8-bugbear>=22,<23',
            'isort>=5,<6',
            'pydocstyle>=6,<7',
            'pylint>=2,<3',
            'toml>=0,<1'
        ]
    }
)
