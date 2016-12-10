
# ----------------------------------------------------------------------
# --- DBmanager.py                                                   ---
# ----------------------------------------------------------------------
# --- This file is meant manage the Data Base                        ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-11-10                                             ---
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# IMPORTS

import sqlite3
import os
from glob import *
from timer import *




# ----------------------------------------------------------------------
# PARAMETERS

# DB_PATH
DB_PATH_REL = 'db'
DB_PATH_FULL = PROCESS.mainPath + '/' + DB_PATH_REL
# DB_FILE_NAME
DB_FILE_NAME = 'autoGarden.db'
DB_FILE_NAME_FULL = DB_PATH_FULL + '/' + DB_FILE_NAME

# DB_TABLES
DB_WEATHER_TABLE = 'WEATHER'


# ----------------------------------------------------------------------
# FUNCTIONS

# -------------------------------------
# DBsetup(DBconn=None, DBcursor=None)
def DBsetup(DBconn=None, DBcursor=None):
	# check if DB_PATH_FULL exists, create it if it does not
	if (not os.path.exists(DB_PATH_FULL)):
		os.makedirs(DB_PATH_FULL)
	if (DBconn==None):
		DBconn = sqlite3.connect(DB_FILE_NAME_FULL)
		DBcursor = DBconn.cursor()
	elif (DBcursor==None):
		DBcursor = DBconn.cursor()
	DBcursor.execute(
	'''
		CREATE TABLE IF NOT EXISTS {} (
			ID INTEGER PRIMARY KEY AUTOINCREMENT,
			DATETIME TEXT NOT NULL,
			TYPE TEXT NOT NULL,
			WPAR TEXT NOT NULL,
			WPARID TEXT NOT NULL,
			VALUE_INT INTEGER,
			VALUE_REA REAL,
			VALUE_STR TEXT
		);
	'''.format(DB_WEATHER_TABLE))
	DBconn.commit()

	
# -------------------------------------
# DBclose(DBconn=None, DBcursor=None)
def DBclose(DBconn=None):
	if (DBconn==None):
		DBconn = sqlite3.connect(DB_FILE_NAME_FULL)
	DBconn.close()
	
	
# -------------------------------------
# DBweatherInsert(DBconn, DBcursor, type, wpar, wparId, valueInt=None, valueReal=None, valueStr=None)
def DBweatherInsert(DBconn, DBcursor, type, wpar, wparId, valueInt=None, valueReal=None, valueStr=None):
	DBparams = (nowDatetime(), type, wpar, wparId, valueInt, valueReal, valueStr)
	DBcursor.execute('INSERT INTO {}(DATETIME,TYPE,WPAR,WPARID,VALUE_INT,VALUE_REA,VALUE_STR) VALUES (?,?,?,?,?,?,?);'.format(DB_WEATHER_TABLE), DBparams)
	DBconn.commit()



