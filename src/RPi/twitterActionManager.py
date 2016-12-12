# -*- coding: utf-8 -*-
# encoding=utf8

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

	# -------------------------------------
	# Twitter API example: get last twitter_tweets from twitter_user and print their text field
	# twitter_user = "PlantitaTest"
	# twitter_tweets = 10
	# twitter_user_timeline = twitter.get_user_timeline(screen_name=twitter_user,count=twitter_tweets)
	# for t in twitter_user_timeline:
		# print (t['text'])
	
	
	# -------------------------------------
	# Twitter API example: get last twitter_mentions of the current user and print this text field
	# twitter_mentions = 10
	# twitter_user_mentions = twitter.get_mentions_timeline(count=twitter_mentions)
	# print "\nTwitting mentions:"
	# for t in twitter_user_mentions:
	# 	print (t['text'])
	# print "Mentions end\n"
	# exit()
	
	
# ----------------------------------------------------------------------
# IMPORTS
import random
import time
import sqlite3
from log import LOG, LOG_DEB, LOG_DET, LOG_INF, LOG_WAR, LOG_ERR, LOG_CRS, LOG_OFF
from action import *
from glob import *
from DBmanager import *
from actionManager import *
from twython import Twython, TwythonError
from passwords import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, IPCAM_NAME, IPCAM_PASS, IPCAM_IP, IPCAM_HOSTDIR
from timer import *
import subprocess
from PIL import Image
from StringIO import StringIO




# ----------------------------------------------------------------------
# FUNCTIONS

# checks if any item from a list is into a second item
# (i.e. (('temp','humi'), 'I love this temperature') -> True)
# (i.e. (('1','2','3')  , '69840')                   -> False)
def itemFromListInItem (listOfItems, item):
	for i in listOfItems:
		if (i in item):
			return True
	return False

	
# tweets a random tweet from the list TWEETS_LIST. Takes care of not repeating a tweet with random appends
def twitterChooseTweetAndUpdateStatus(twitter, TWEETS_LIST, formatValue=None, tm_reply_user=None, tm_reply_id=None, tm_media=None):

	# parameters
	TWEETS_LIST_COPY = list(TWEETS_LIST)
	errorDuplicate = "Status is a duplicate"
	tweetText = ""
	tweetItem = ""
	repeatedTweetAppend = " ({0:03d})"
	repeatedTweetMode = False
	repeatedTweetAttempts = 0
	repeatedTweetLimit = 15
	
	# while loop
	while (True):
		
		# check if we already tried all the possible tweets in TWEETS_LIST_COPY, if so, add a random number as append
		if (len(TWEETS_LIST_COPY)==0):
			if (len(tweetItem)==0):
				LOG(LOG_ERR, "<<< ERROR: in twitterChooseTweetAndUpdateStatus(): tweetItem never initialized, TWEETS_LIST empty? >>>")
				return False
			repeatedTweetAttempts += 1
			if (repeatedTweetAttempts >= repeatedTweetLimit):
				LOG(LOG_ERR, "<<< ERROR: in twitterChooseTweetAndUpdateStatus(): repeatedTweetLimit reached >>>")
				return False
			repeatedTweetAppend = repeatedTweetAppend.format(random.randint(0, 999))
			if (not repeatedTweetMode):
				repeatedTweetMode = True
				tweetItem = "{}{}".format(tweetItem, repeatedTweetAppend)
			else:
				tweetItem = "{}{}".format(tweetItem[0:len(tweetItem)-len(repeatedTweetAppend)], repeatedTweetAppend)

		# set tweetText, according to tm_reply_user (update or mention)
		if (not repeatedTweetMode):
			tweetItem = random.choice(TWEETS_LIST_COPY)
			TWEETS_LIST_COPY.remove(tweetItem)
		if ((tm_reply_user is not None) and (tm_reply_id is not None)):
			tweetText = "@{}, {}{}".format(tm_reply_user, tweetItem[0].lower(), tweetItem[1:])
		else: 
			tweetText = tweetItem
		
		# format tweetText, according to formatValue
		if (formatValue is not None):
			tweetText = tweetText.format(formatValue)
		
		# try to tweet
		try:
			if ((tm_reply_user is not None) and (tm_reply_id is not None)):
				if (tm_media is not None):
					twitter.update_status(status=tweetText, in_reply_to_status_id=tm_reply_id, media_ids=tm_media)
				else:
					twitter.update_status(status=tweetText, in_reply_to_status_id=tm_reply_id)
			else:
				if (tm_media is not None):
					twitter.update_status(status=tweetText, media_ids=tm_media)
				else:
					twitter.update_status(status=tweetText)
			LOG(LOG_INF,"Twitted succesfully: \"{}\"".format(tweetText), logPreLn=True)
			return True
		except TwythonError as e:
			if (errorDuplicate in e):
				LOG(LOG_WAR,"<<< WARNING: TwythonError: \"{}\" >>>".format(e), logPreLn=True)
			else:
				LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e), logPreLn=True)
				return False
		except:
			LOG(LOG_ERR,"<<< ERROR: UnkownError in twitterChooseTweetAndUpdateStatus() >>>", logPreLn=True)
			return False
	
	
# -------------------------------------
# txTwitterActionManager()
# Checks the DB and twitter and generates and action, if needed.
# This function is meant to be a thread
def txTwitterActionManager():

	# wait for rx setup
	time.sleep(2.000)
	
	# parameters: DBconn, DBcursor
	DBconn = sqlite3.connect(DB_FILE_NAME_FULL)
	DBcursor = DBconn.cursor()
	DBqueryWeatherOne = 'SELECT VALUE_REA FROM WEATHER WHERE WPAR=\'{}\' AND WPARID=\'{}\' AND TYPE=\'{}\' ORDER BY DATETIME DESC LIMIT 1;'
	
	# parameters: Timer related
	twitter_window_offset = 1.1
	twitter_window_mins = 15.0
	get_mentions_timeline_limit = 75.0
	get_mentions_timeline_periodMin = (twitter_window_mins / get_mentions_timeline_limit) * twitter_window_offset
	
	# parameters: timers
	timer_tweet_TEMP_DHT = Timer(periodMins=240.0)
	timer_mentions = Timer(periodMins=get_mentions_timeline_periodMin)
	
	# parameters: ip camera
	ipCamFileNameDef = 'ipcam_{}.jpg'
	ipCamPathRel = 'cam'
	ipCamPathFull = PROCESS.mainPath + '/' + ipCamPathRel
	ipCamScriptDef = 'avconv -y -i "rtsp://{}:{}@{}/{}" -q:v 9 -s 1280x720 -vframes 1 {}/'.format(IPCAM_NAME, IPCAM_PASS, IPCAM_IP, IPCAM_HOSTDIR, ipCamPathFull) + '{}'
	
	# parameters: twitter, tm (twitter_mention)
	tweetText = ''
	twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	tm_count = 20
	tm_List = [] 
	tm_last_List = []
	tm_new_List = [] 
	tm_replied = False
	
	# setup: create initial tx and rx
	rxTwitterAction.set()
	txTwitterAction.set()
	txTwitterAction.setId(intToId(ACTION_TWITTER_ID - ACTION_TYPES_GLOBAL*2))	# ready for autoincrement
	
	# loop: check timers and twitter, updating txTwitterAction if so
	while (STATUS.get("isAlive")):
		
		# delay
		time.sleep(1.0)
		LOG(LOG_DET, "TWITTER: checking status...")
		
		# check STATUS.get("twitterEnable")
		if (not STATUS.get("twitterEnable")):
			continue
		LOG(LOG_DET, "TWITTER: status OK...")

		# MENTIONS MANAGEMENT
		if (timer_mentions.isReady()):
		
			LOG(LOG_DET, "TWITTER: timer OK...")
			
			# get last mentions
			try:
				tm_List = list(twitter.get_mentions_timeline(count=tm_count))
			except TwythonError as e:
				LOG(LOG_ERR,"<<< ERROR: TwythonError in twitter.get_mentions_timeline({}): \"{}\" >>>".format(tm_count, e), logPreLn=True)
				continue
			LOG(LOG_DET, "TWITTER: got last mentions...")
			
			# get tm_new_List, update tm_last_List 
			tm_new_List = []
			# initialize tm_last_List, just the first time it's executed
			if (len(tm_last_List) <= 0):
				for tm in tm_List:
					tm_last_List.append(tm['id'])
			# fill tm_new_List with the new mentions
			for tm in tm_List:
				if(tm['id'] not in tm_last_List):
					tm_new_List.append(tm)
			# update tm_new_List (if so)
			if (len(tm_new_List) > 0):
				tm_last_List = []
				for tm in tm_List:
					tm_last_List.append(tm['id'])
			
			# explore tm_new_List
			for tm in tm_new_List:
			
				# set twitter_mention parameters
				tm_id = tm['id']
				tm_user_screen_name = tm['user']['screen_name']
				tm_text = tm['text']
				tm_text_lower = tm_text.lower()
				tm_replied = False
				LOG(LOG_DET, "TWITTER: new mention: {}".format(tm_text))

				# MENTIONS: TEMP DHT
				# itemFromListInItem (listOfItems, item):
				if (itemFromListInItem(TWEETDATA.get('TEMP', 'TEXT', 'ENG', 0), tm_text_lower) or itemFromListInItem(TWEETDATA.get('TEMP', 'TEXT', 'SPA', 0), tm_text_lower)):
				
					# get new parameter to DB (set tx action and wait rx action)
					if (not getToDB(WPAR_TEMP_L, WPARID_TEMP_DHT_L, type=TYPE_TWITTER_L)):
						continue
					
					# get last TEMP_DHT temperature from DB
					DBcursor.execute(DBqueryWeatherOne.format(WPAR_TEMP_L, WPARID_TEMP_DHT_L, TYPE_TWITTER_L))
					DBrow = DBcursor.fetchone()
					
					# make a tweet about the TEMP_DHT
					if (DBrow is not None):
						TEMP_value = DBrow[0]
						TEMP_limit_idx = 0
						if (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 0)):
							TEMP_limit_idx = 0
						elif (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 1)):
							TEMP_limit_idx = 1
						elif (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 2)):
							TEMP_limit_idx = 2
						elif (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 3)):
							TEMP_limit_idx = 3
						elif (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 4)):
							TEMP_limit_idx = 4
						else:
							TEMP_limit_idx = 5
						tm_r = twitterChooseTweetAndUpdateStatus(twitter, TWEETDATA.get('TEMP', 'TWEET', 'SPA', TEMP_limit_idx), formatValue=TEMP_value, tm_reply_user=tm_user_screen_name, tm_reply_id=tm_id)
						tm_replied = tm_replied or tm_r
					else:
						LOG(LOG_WAR,"<<< WARNING: No rows found in DB (txTwitterActionManager, WEATHER, TEMP) >>>", logPreLn=True)
						
				# MENTIONS: HUMI DHT
				if (itemFromListInItem(TWEETDATA.get('HUMI', 'TEXT', 'ENG', 0), tm_text_lower) or itemFromListInItem(TWEETDATA.get('HUMI', 'TEXT', 'SPA', 0), tm_text_lower)):
				
					# get new parameter to DB (set tx action and wait rx action)
					if (not getToDB(WPAR_HUMI_L, WPARID_HUMI_DHT_L, type=TYPE_TWITTER_L)):
						continue
					
					# get last TEMP_DHT temperature from DB
					DBcursor.execute(DBqueryWeatherOne.format(WPAR_HUMI_L, WPARID_HUMI_DHT_L, TYPE_TWITTER_L))
					DBrow = DBcursor.fetchone()

					# make a tweet about the TEMP_DHT
					if (DBrow is not None):
						HUMI_value = DBrow[0]
						HUMI_limit_idx = 0
						if (HUMI_value < TWEETDATA.get('HUMI', 'LIMIT_MAX', 0)):
							HUMI_limit_idx = 0
						elif (HUMI_value < TWEETDATA.get('HUMI', 'LIMIT_MAX', 1)):
							HUMI_limit_idx = 1
						else:
							HUMI_limit_idx = 2
						tm_r = twitterChooseTweetAndUpdateStatus(twitter, TWEETDATA.get('HUMI', 'TWEET', 'SPA', HUMI_limit_idx), formatValue=HUMI_value, tm_reply_user=tm_user_screen_name, tm_reply_id=tm_id)
						tm_replied = tm_replied or tm_r
					else:
						LOG(LOG_WAR,"<<< WARNING: No rows found in DB (txTwitterActionManager, WEATHER, HUMI) >>>", logPreLn=True)
						
				# MENTIONS: RAIN MH
				if (itemFromListInItem(TWEETDATA.get('RAIN', 'TEXT', 'ENG', 0), tm_text_lower) or itemFromListInItem(TWEETDATA.get('RAIN', 'TEXT', 'SPA', 0), tm_text_lower)):
					
					# get new parameter to DB (set tx action and wait rx action)
					RAIN_MH_time = 1500
					RAIN_MH_period = 50
					if (not getToDB(WPAR_RAIN_L, WPARID_RAIN_MH_L, type=TYPE_TWITTER_L, append=',{},{}'.format(RAIN_MH_time, RAIN_MH_period))):
						continue
					
					# get last TEMP_DHT temperature from DB
					DBcursor.execute(DBqueryWeatherOne.format(WPAR_RAIN_L, WPARID_RAIN_MH_L, TYPE_TWITTER_L))
					DBrow = DBcursor.fetchone()

					# make a tweet about the TEMP_DHT
					if (DBrow is not None):
						RAIN_value = DBrow[0]
						RAIN_limit_idx = 0
						if (RAIN_value < TWEETDATA.get('RAIN', 'LIMIT_MAX', 0)):
							RAIN_limit_idx = 0
						else:
							RAIN_limit_idx = 1
						tm_r = twitterChooseTweetAndUpdateStatus(twitter, TWEETDATA.get('RAIN', 'TWEET', 'SPA', RAIN_limit_idx), tm_reply_user=tm_user_screen_name, tm_reply_id=tm_id)
						tm_replied = tm_replied or tm_r
					else:
						LOG(LOG_WAR,"<<< WARNING: No rows found in DB (txTwitterActionManager, WEATHER, RAIN) >>>", logPreLn=True)
						
				# MENTIONS: PHOTO
				if (itemFromListInItem(TWEETDATA.get('PHOTO', 'TEXT', 'ENG', 0), tm_text_lower) or itemFromListInItem(TWEETDATA.get('PHOTO', 'TEXT', 'SPA', 0), tm_text_lower)):
					
					# get file and script names
					ipCamFileName = ipCamFileNameDef.format(nowDatetime('%Y%m%d_%H%M%S'))
					ipCamFileNameFull = ipCamPathFull + '/' + ipCamFileName
					ipCamScript = ipCamScriptDef.format(ipCamFileName)
					
					try:
						# call to the process to get the image from the ip cam
						LOG(LOG_DET, "TWITTER: about to execute ipCamScript: {}".format(ipCamScript))
						subprocess.call(ipCamScript, shell=True)
						LOG(LOG_DET, "TWITTER: ipCamScript OK")

						# get the image ready for the tweet
						# https://twython.readthedocs.io/en/latest/usage/advanced_usage.html#updating-status-with-image
						LOG(LOG_DET, "TWITTER: Image.open(ipCamFileNameFull)...")
						photo = Image.open(ipCamFileNameFull)
						LOG(LOG_DET, "TWITTER: Image.open(ipCamFileNameFull) OK")
						# ipCam lies on its left side: rotate 90 (anti-clockwise / to the left)
						LOG(LOG_DET, "TWITTER: photo.rotate...")
						photo = photo.rotate(STATUS.get("ipCamRotation"))
						LOG(LOG_DET, "TWITTER: photo.rotate OK")
						# basewidth = 320
						# wpercent = (basewidth / float(photo.size[0]))
						# height = int((float(photo.size[1]) * float(wpercent)))
						# photo = photo.resize((basewidth, height), Image.ANTIALIAS)
						LOG(LOG_DET, "TWITTER: image_io = StringIO()...")
						image_io = StringIO()
						LOG(LOG_DET, "TWITTER: image_io = StringIO() OK")
						LOG(LOG_DET, "TWITTER: image_io = photo.save(image_io, format='JPEG')...")
						photo.save(image_io, format='JPEG')
						LOG(LOG_DET, "TWITTER: image_io = photo.save(image_io, format='JPEG') OK")
						LOG(LOG_DET, "TWITTER: image_io = photo.save(image_io, image_io.seek(0)...")
						image_io.seek(0)
						LOG(LOG_DET, "TWITTER: image_io = photo.save(image_io, image_io.seek(0) OK")
						LOG(LOG_DET, "TWITTER: image_io = response ...")
						response = twitter.upload_media(media=image_io)
						LOG(LOG_DET, "TWITTER: image_io = response OK")
						
						# make a tweet about the photo
						tm_r = twitterChooseTweetAndUpdateStatus(twitter, TWEETDATA.get('PHOTO', 'TWEET', 'SPA', 0), tm_reply_user=tm_user_screen_name, tm_reply_id=tm_id, tm_media=[response['media_id']])
						tm_replied = tm_replied or tm_r
						
					except:
						LOG(LOG_ERR,"<<< ERROR: ipCam error: \"{}\" >>>".format("unknown error"), logPreLn=True)
						tm_r = twitterChooseTweetAndUpdateStatus(twitter, TWEETDATA.get('PHOTO', 'TWEET', 'SPA', 1), tm_reply_user=tm_user_screen_name, tm_reply_id=tm_id)
						tm_replied = tm_replied or tm_r
				
				# MENTIONS: OTHER
				if (len(TWEETDATA.get('OTHER', 'TEXT', 'SPA')) > 0):
					for idx in range(0, len(TWEETDATA.get('OTHER', 'TEXT', 'SPA'))):
						if (itemFromListInItem(TWEETDATA.get('OTHER', 'TEXT', 'SPA', idx), tm_text_lower)):
							tm_r = twitterChooseTweetAndUpdateStatus(twitter, TWEETDATA.get('OTHER', 'TWEET', 'SPA', idx), tm_reply_user=tm_user_screen_name, tm_reply_id=tm_id)
							tm_replied = tm_replied or tm_r
				
				# MENTIONS: DEFAULT
				if (not tm_replied): 
					tm_r0 = twitterChooseTweetAndUpdateStatus(twitter, TWEETDATA.get('DEFAULT', 'TWEET', 'SPA', 0), tm_reply_user=tm_user_screen_name, tm_reply_id=tm_id)
					tm_r1 = twitterChooseTweetAndUpdateStatus(twitter, TWEETDATA.get('DEFAULT', 'TWEET', 'SPA', 1), tm_reply_user=tm_user_screen_name, tm_reply_id=tm_id)
					tm_replied = tm_replied or tm_r0 or tm_r1
				
		# AUTO TWEETS MANAGEMENT
		
		# TEMP_DHT management
		if (timer_tweet_TEMP_DHT.isReady()):
		
			# get new parameter to DB (set tx action and wait rx action)
			if (not getToDB(WPAR_TEMP_L, WPARID_TEMP_DHT_L, type=TYPE_TWITTER_L)):
				continue
			
			# get last TEMP_DHT temperature from DB
			DBcursor.execute(DBqueryWeatherOne.format(WPAR_TEMP_L, WPARID_TEMP_DHT_L, TYPE_TWITTER_L))
			DBrow = DBcursor.fetchone()
			
			# make a tweet about the TEMP_DHT
			if (DBrow is not None):
				TEMP_value = DBrow[0]
				TEMP_limit_idx = 0
				if (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 0)):
					TEMP_limit_idx = 0
				elif (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 1)):
					TEMP_limit_idx = 1
				elif (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 2)):
					TEMP_limit_idx = 2
				elif (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 3)):
					TEMP_limit_idx = 3
				elif (TEMP_value < TWEETDATA.get('TEMP', 'LIMIT_MAX', 4)):
					TEMP_limit_idx = 4
				else:
					TEMP_limit_idx = 5
				twitterChooseTweetAndUpdateStatus(twitter, TWEETDATA.get('TEMP', 'TWEET', 'SPA', TEMP_limit_idx), formatValue=TEMP_value)
			else:
				LOG(LOG_WAR,"<<< WARNING: No rows found in DB (txTwitterActionManager, WEATHER, TEMP) >>>", logPreLn=True)
			

