# https://stackoverflow.com/questions/14975018/creating-single-exe-using-py2exe-for-a-tkinter-program
from distutils.core import setup
import py2exe

setup(windows=[{'script': 'grapheur.py'}])