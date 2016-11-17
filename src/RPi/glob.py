# ----------------------------------------------------------------------
# --- global.cpp                                                     ---
# ----------------------------------------------------------------------
# --- Global variables     										     ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-10-25                                             ---
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# IMPORTS
import inspect
import os


# ----------------------------------------------------------------------
# CLASS PROCESS
class Process:
	isAlive = True
	mainPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	def __init__(self):
		self.isAlive = True
		mainPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

		
# ----------------------------------------------------------------------
# PARAMETERS GLOBAL
PROCESS = Process()

