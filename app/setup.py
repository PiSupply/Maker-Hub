#!/usr/bin/env python
from distutils.core import setup
import glob
import os
import sys

setup(
	name = "MakerHub",
	version = "0.1.0",
	author = "Denis Khrutsky",
	author_email = "denis.xpy@gmail.com",
	description = "Installer for PiSupply products software",
	url = "https://github.com/PiSupply/MakerHub",
	license='GPL v2',
	packages=['makerhub'],
	py_modules=[''],
	data_files=[
        ('share/applications', ['data/makerhub-gui.desktop']),
        ('share/makerhub/images', glob.glob('data/media/*')),
        ('share/makerhub/', ['data/packages.json']),
    ],
	scripts = ['bin/makerhub_gui.py', 'bin/makerhub_console.py'],
    install_requires=[
        "urwid >= 1.3.1",
        "PyQt5 >= 5.0",
    ],
	)
