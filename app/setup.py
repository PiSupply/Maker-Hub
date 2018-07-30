#!/usr/bin/env python
from setuptools import setup
import glob
import os
import sys

setup(
	name = "MakerHub",
	version = "0.2.0",
	author = "Ilya Starodubtsev",
	author_email = "kentbrokmen55@gmail.com",
	description = "Installer for PiSupply products software",
	url = "https://github.com/PiSupply/MakerHub",
	license='GPL v2',
	packages=['makerhub'],
	py_modules=[''],
	data_files=[
        ('share/applications', ['data/makerhub-gui.desktop']),
        ('share/makerhub/data/media', glob.glob('data/media/*')),
        ('share/makerhub/', ['data/packages.json']),
	('share/makerhub/data',['data/main.qml']),
    ],
	scripts = ['bin/makerhub_gui.py', 'bin/makerhub_console.py'],
    install_requires=[
	"urwid >= 1.3.1",
	"PyQt5 >= 5.0",

    ],
	)
