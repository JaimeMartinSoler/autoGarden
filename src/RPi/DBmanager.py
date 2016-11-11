
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




# ----------------------------------------------------------------------
# PARAMETERS

DB_PATH = 'db'
DB_NAME = 'autoGarden.db'
DB_FULL_PATH = DB_PATH + '/' + DB_NAME




# ----------------------------------------------------------------------
# FUNCTIONS

# -------------------------------------
# DBsetup(DBconn=None, DBcursor=None)
def DBsetup(DBconn=None, DBcursor=None):
	if (not os.path.exists(DB_PATH)):
		os.makedirs(DB_PATH)
	if (DBconn==None):
		DBconn = sqlite3.connect(DB_FULL_PATH)
		DBcursor = DBconn.cursor()
	elif (DBcursor==None):
		DBcursor = DBconn.cursor()
	DBcursor.execute('''
		CREATE TABLE IF NOT EXISTS WEATHER (
			ID INTEGER PRIMARY KEY AUTOINCREMENT,
			DATETIME TEXT NOT NULL,
			TYPE TEXT NOT NULL,
			WPAR TEXT NOT NULL,
			WPARID TEXT NOT NULL,
			VALUE_INT INTEGER,
			VALUE_REA REAL,
			VALUE_STR TEXT
		);
	''')
	DBconn.commit()

	
# -------------------------------------
# DBclose(DBconn=None, DBcursor=None)
def DBclose(DBconn=None):
	if (DBconn==None):
		DBconn = sqlite3.connect(DB_FULL_PATH)
	DBconn.close()
	
	
# -------------------------------------
# DBinsert(DBconn, DBcursor, type, wpar, wparId, valueInt=None, valueReal=None, valueStr=None)
def DBinsert(DBconn, DBcursor, type, wpar, wparId, valueInt=None, valueReal=None, valueStr=None):
	DBparams = (nowDatetime(), type, wpar, wparId, valueInt, valueReal, valueStr)
	DBcursor.execute('INSERT INTO WEATHER(DATETIME,TYPE,WPAR,WPARID,VALUE_INT,VALUE_REA,VALUE_STR) VALUES (?,?,?,?,?,?,?);', DBparams)
	DBconn.commit()

