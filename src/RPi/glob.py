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
from action import Action, idAdd




# ----------------------------------------------------------------------
# PARAMETERS
rxAction = Action()			# Action for RX general propose
rxNormalAction = Action()	# Action for RX Normal actions, answers to requests from RPi DB,timers checking module
rxTwitterAction = Action()	# Action for RX Twitter actions, answers to requests from RPi Twitter checking module
rxArduinoAction = Action()	# Action for RX Arduino actions, urgents messages sent by Arduino
txNormalAction = Action()	# Action for TX Normal actions, requests from RPi DB,timers checking module
txTwitterAction = Action()	# Action for TX Twitter actions, requests from RPi Twitter checking module
