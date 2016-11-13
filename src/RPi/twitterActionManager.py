
# ----------------------------------------------------------------------
# --- twitterActionManager.py                                        ---
# ----------------------------------------------------------------------
# --- This file is meant to manage the txTwitterAction object,       ---
# --- checking timers and database to request more info and tweet    ---
# ----------------------------------------------------------------------
# --- Author: Jaime Martin Soler                                     ---
# --- Date  : 2016-11-11                                             ---
# ----------------------------------------------------------------------

# Twitter API: https://dev.twitter.com/overview/api/tweets
# Twython: http://twython.readthedocs.io/en/latest/api.html?highlight=get_user_timeline
# example: http://www.craigaddyman.com/mining-all-tweets-with-python/

# ----------------------------------------------------------------------
# IMPORTS
import random
import time
import sqlite3
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
from action import *
from glob import *
from DBmanager import *
from twython import Twython, TwythonError
from twitterPass import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET




# ----------------------------------------------------------------------
# FUNCTIONS

# -------------------------------------
# txTwitterActionManager()
# Checks the DB and twitter and generates and action, if needed.
# This function is meant to be a thread
def txTwitterActionManager():

	# wait for rx setup
	time.sleep(2.000)
	
	# parameters: DBconn, DBcursor
	DBconn = sqlite3.connect(DB_PATH_FULL)
	DBcursor = DBconn.cursor()
	# parameters: id counters
	countId = 200000
	# parameters: timers
	TEMP_AIR_period = 30.0							# TEMP_AIR_period in minutes
	TEMP_AIR_period_j = TEMP_AIR_period/(1440.0)	# TEMP_AIR_period in julian
	TEMP_AIR_last_j = 0.0
	TWITTER_period = 1.1						# TWITTER_period in minutes
	TWITTER_period_j = TWITTER_period/(1440.0)	# TWITTER_period_j in julian
	TWITTER_last_j = 0.0
	# parameters: twitter
	twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	twitter_mention = []
	# parameters: MENTIONS
	twitter_mention_text_last = ""
	# parameters: TEMP_AIR_TWEETS
	TEMP_AIR_TWEETS = [
		"Oh dear, the temperature is {:.1f} celsius, that is so grateful!",
		"I'm willing to inform that temperature is {:.1f} celsius.",
		"Do you see? Temperature is {:.1f} celsius, my dear sweety darling.",
		"It is so wonderful this temperature of {:.1f} celsius. Marvelous!",
		"Such a warmy day, it is {:.1f} celsius, wonderful!"
	]
	
	# -------------------------------------
	# Twitter API example: get last twitter_tweets from twitter_user and print their text field
	# twitter_user = "PlantitaTest"
	# twitter_tweets = 10
	# twitter_user_timeline = twitter.get_user_timeline(screen_name=twitter_user,count=twitter_tweets)
	# for t in twitter_user_timeline:
		# print (t['text'])
	
	
	# -------------------------------------
	# Twitter API example: get last twitter_mentions of the current user and print theis text field
	# twitter_mentions = 10
	# twitter_user_mentions = twitter.get_mentions_timeline(count=twitter_mentions)
	# print "\nTwitting mentions:"
	# for t in twitter_user_mentions:
	# 	print (t['text'])
	# print "Mentions end\n"
	# exit()
	
	# setup: create a fake (txSuccess=1) to avoid tx and jump wait loop
	txTwitterAction.txSuccess = 1
	txTwitterAction.txReadyToTx = True
	
	# loop: check timers and twitter, updating txTwitterAction if so
	while (PROCESS.isAlive):
		
		# wait for previous action to be transmitted and received
		while((txTwitterAction.txReadyToTx and txTwitterAction.txSuccess<=0) or (rxTwitterAction.rxReadyToExec and rxTwitterAction.rxExec<=0)):
			# Check PROCESS.isAlive
			if (not PROCESS.isAlive):
				return
			time.sleep(0.100)
		nowJulianDT = nowJulian()
		
		# MENTIONS MANAGEMENT
		if ((nowJulianDT - TWITTER_last_j) >= TWITTER_period_j):
			TWITTER_last_j = nowJulianDT
			try:
				twitter_mention = twitter.get_mentions_timeline(count=1)[0]
			except TwythonError as e:
				LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e))
				continue
			twitter_mention_id = twitter_mention['id']
			twitter_mention_user_screen_name = twitter_mention['user']['screen_name']
			twitter_mention_text = twitter_mention['text']
			if (twitter_mention_text != twitter_mention_text_last):
				twitter_mention_text_last = twitter_mention_text
				# MENTIONS: TEMP_AIR
				twitter_mention_text_last_lower = twitter_mention_text_last.lower()
				if ("temp" in twitter_mention_text_last_lower):
					# clear rx and set tx objects
					rxTwitterAction.set()
					txTwitterAction.set(intToId(countId)+",R0,A0,TW,GET,TEMP,AIR")
					txTwitterAction.txReadyToTx = True
					countId += 1
					while((txTwitterAction.txReadyToTx and txTwitterAction.txSuccess<=0) or (rxTwitterAction.rxReadyToExec and rxTwitterAction.rxExec<=0)):
						# Check PROCESS.isAlive
						if (not PROCESS.isAlive):
							return
						time.sleep(0.100)
					# get last TEMP_AIR temperature from DB
					DBcursor.execute('SELECT * FROM WEATHER WHERE WPAR=\'TEMP\' AND WPARID=\'AIR\' ORDER BY DATETIME DESC LIMIT 1;')
					DBrow = DBcursor.fetchone()
					# make a tweet about the TEMP_AIR
					if (DBrow is not None):
						TEMP_AIR_value = DBrow[6]
						tweetText = "@" + twitter_mention_user_screen_name + ", " + random.choice(TEMP_AIR_TWEETS).format(TEMP_AIR_value)
						try:
							twitter.update_status(status=tweetText, in_reply_to_status_id=twitter_mention_id)
							LOG(LOG_INF,"Twitted succesfully: \"{}\"".format(tweetText))
						except TwythonError as e:
							LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e))
		
		# AUTO TWEETS MANAGEMENT
		
		# TEMP_AIR management
		if ((nowJulianDT - TEMP_AIR_last_j) >= TEMP_AIR_period_j):
			# get last TEMP_AIR temperature from DB
			DBcursor.execute('SELECT * FROM WEATHER WHERE WPAR=\'TEMP\' AND WPARID=\'AIR\' ORDER BY DATETIME DESC LIMIT 1;')
			DBrow = DBcursor.fetchone()
			# make a tweet about the TEMP_AIR
			if (DBrow is not None):
				TEMP_AIR_last_j = nowJulianDT
				TEMP_AIR_value = DBrow[6]
				tweetText = random.choice(TEMP_AIR_TWEETS).format(TEMP_AIR_value)
				try:
					twitter.update_status(status=tweetText)
					LOG(LOG_INF,"Twitted succesfully: \"{}\"".format(tweetText))
				except TwythonError as e:
					LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e))
			else:
				LOG(LOG_WAR,"<<< WARNING: No rows found in DB (txTwitterActionManager, WEATHER) >>>")
			
		# delay
		time.sleep(1.0)

