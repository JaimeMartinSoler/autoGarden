
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
from actionManager import *
from twython import Twython, TwythonError
from passwords import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, IPCAM_NAME, IPCAM_PASS, IPCAM_IP, IPCAM_HOSTDIR
from timer import *
import subprocess
from PIL import Image
from StringIO import StringIO



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
	DBconn = sqlite3.connect(DB_FILE_NAME_FULL)
	DBcursor = DBconn.cursor()
	
	# parameters: timers
	timer_tweet_TEMP_DHT = Timer(periodMins=240.0)
	timer_mentions = Timer(periodMins=1.1)
	
	# parameters: ip camera
	ipCamFileNameDef = 'ipcam_{}.jpg'
	ipCamPathRel = 'cam'
	ipCamPathFull = PROCESS.mainPath + '/' + ipCamPathRel
	ipCamScriptDef = 'avconv -y -i "rtsp://{}:{}@{}/{}" -q:v 9 -s 1280x720 -vframes 1 {}/'.format(IPCAM_NAME, IPCAM_PASS, IPCAM_IP, IPCAM_HOSTDIR, ipCamPathFull) + '{}'
	
	# parameters: twitter
	twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	twitter_mention = []
	
	# parameters: MENTIONS
	twitter_mention_text_last = ""
	# parameters: TEMP_TWEETS
	TEMP_TWEETS = [
		"Oh my dear, the temperature is {:.1f} celsius, that is so grateful!",
		"I like to inform that temperature is {:.1f} celsius",
		"Can you see? Temperature is {:.1f} celsius, my dear sweety darling",
		"It's so wonderful this temperature of {:.1f} celsius. Marvelous!",
		"Such a nice day, it is {:.1f} celsius, wonderful!"
	]
	HUMI_TWEETS = [
		"Oh my dear, the humidity is {:.1f}%, that is so grateful!",
		"I like to inform that humidity is {:.1f}%",
		"Can you see? Humidity is {:.1f}%, my dear sweety darling",
		"It's so wonderful this humidity {:.1f}%. Marvelous!",
		"Such a nice day, humidity is {:.1f}%, wonderful!"
	]
	RAIN_TWEETS = [
		"Oh my dear, it's{} raining, that is so grateful!",
		"I like to inform that it's{} raining",
		"Can you see? it's{} raining, my dear sweety darling",
		"It's so wonderful that it's{} raining. Marvelous!",
		"Such a nice day, it's{} raining, wonderful!"
	]
	RAIN_THRESHOLD = 30.0
	RAIN_TEXT = ""
	RAIN_TEXT_YES = ""
	RAIN_TEXT_NO = " NOT"
	DEFAULT_TWEETS = [
		"Hi there, I'm an automatic plant, mention me asking about my 'temperature', 'humidity' or the 'rain'",
		"If you mention me asking about my 'temperature', 'humidity' or the 'rain' I will automatically answer",
		"Try to mention me asking about my 'temperature', 'humidity' or the 'rain' I will answer by myself"
	]
	
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
	
	# setup: create initial tx and rx
	rxTwitterAction.set()
	txTwitterAction.set()
	txTwitterAction.setId(intToId(ACTION_TWITTER_ID - ACTION_TYPES_GLOBAL*2))	# ready for autoincrement
	
	# loop: check timers and twitter, updating txTwitterAction if so
	while (PROCESS.isAlive):
		
		# delay
		time.sleep(1.0)

		# MENTIONS MANAGEMENT
		if (timer_mentions.isReady()):
			
			# get last mention
			try:
				twitter_mention = twitter.get_mentions_timeline(count=1)[0]
			except TwythonError as e:
				LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e), logPreLn=True)
				continue
			twitter_mention_id = twitter_mention['id']
			twitter_mention_user_screen_name = twitter_mention['user']['screen_name']
			twitter_mention_text = twitter_mention['text']
			if (twitter_mention_text != twitter_mention_text_last):
				twitter_mention_text_last = twitter_mention_text
				twitter_mention_text_last_lower = twitter_mention_text_last.lower()

				# MENTIONS: TEMP DHT
				if ("temp" in twitter_mention_text_last_lower):
				
					# set tx action and wait rx action
					try:
						setTXwaitRX(txTwitterAction, rxTwitterAction, "XXX,R,A,T,G,TEMP,DHT", timeOut=5000, autoIncrement=True, checkRXid=True)
					except RuntimeError:	# if (not PROCESS.isAlive)
						return
					except OSError as te:	# if (Timeout)
						LOG(LOG_ERR,"<<< WARNING: TwitterAction TimeoutError: \"{}\" >>>".format(te), logPreLn=True)
						continue
					except ValueError as ve:	# if (rx.ID is not as expected)
						LOG(LOG_ERR,"<<< WARNING: rxTwitterAction ValueError: \"{}\" >>>".format(ve), logPreLn=True)
						continue
						
					# get last TEMP_DHT temperature from DB
					DBcursor.execute('SELECT * FROM WEATHER WHERE WPAR=\'TEMP\' AND WPARID=\'DHT\' ORDER BY DATETIME DESC LIMIT 1;')
					DBrow = DBcursor.fetchone()
					
					# make a tweet about the TEMP_DHT
					if (DBrow is not None):
						TEMP_value = DBrow[6]
						tweetText = "@" + twitter_mention_user_screen_name + ", " + random.choice(TEMP_TWEETS).format(TEMP_value)
						try:
							twitter.update_status(status=tweetText, in_reply_to_status_id=twitter_mention_id)
							LOG(LOG_INF,"Twitted succesfully: \"{}\"".format(tweetText), logPreLn=True)
						except TwythonError as e:
							LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e), logPreLn=True)
		
				# MENTIONS: HUMI DHT
				elif (("humidity" in twitter_mention_text_last_lower) or ("humedad" in twitter_mention_text_last_lower)):
				
					# set tx action and wait rx action
					try:
						setTXwaitRX(txTwitterAction, rxTwitterAction, "XXX,R,A,T,G,HUMI,DHT", timeOut=5000, autoIncrement=True, checkRXid=True)
					except RuntimeError:	# if (not PROCESS.isAlive)
						return
					except OSError as te:	# if (Timeout)
						LOG(LOG_ERR,"<<< WARNING: TwitterAction TimeoutError: \"{}\" >>>".format(te), logPreLn=True)
						continue
					except ValueError as ve:	# if (rx.ID is not as expected)
						LOG(LOG_ERR,"<<< WARNING: rxTwitterAction ValueError: \"{}\" >>>".format(ve), logPreLn=True)
						continue
						
					# get last TEMP_DHT temperature from DB
					DBcursor.execute('SELECT * FROM WEATHER WHERE WPAR=\'HUMI\' AND WPARID=\'DHT\' ORDER BY DATETIME DESC LIMIT 1;')
					DBrow = DBcursor.fetchone()
					
					# make a tweet about the TEMP_DHT
					if (DBrow is not None):
						HUMI_value = DBrow[6]
						tweetText = "@" + twitter_mention_user_screen_name + ", " + random.choice(HUMI_TWEETS).format(HUMI_value)
						try:
							twitter.update_status(status=tweetText, in_reply_to_status_id=twitter_mention_id)
							LOG(LOG_INF,"Twitted succesfully: \"{}\"".format(tweetText), logPreLn=True)
						except TwythonError as e:
							LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e), logPreLn=True)
		
				# MENTIONS: RAIN MH
				elif (("rain" in twitter_mention_text_last_lower) or ("llueve" in twitter_mention_text_last_lower) or ("lluvi" in twitter_mention_text_last_lower) or ("llov" in twitter_mention_text_last_lower)):
				
					# set tx action and wait rx action
					try:
						setTXwaitRX(txTwitterAction, rxTwitterAction, "XXX,R,A,T,G,RAIN,MH,1000,20", timeOut=5000, autoIncrement=True, checkRXid=True)
					except RuntimeError:	# if (not PROCESS.isAlive)
						return
					except OSError as te:	# if (Timeout)
						LOG(LOG_ERR,"<<< WARNING: TwitterAction TimeoutError: \"{}\" >>>".format(te), logPreLn=True)
						continue
					except ValueError as ve:	# if (rx.ID is not as expected)
						LOG(LOG_ERR,"<<< WARNING: rxTwitterAction ValueError: \"{}\" >>>".format(ve), logPreLn=True)
						continue
						
					# get last TEMP_DHT temperature from DB
					DBcursor.execute('SELECT * FROM WEATHER WHERE WPAR=\'RAIN\' AND WPARID=\'MH\' ORDER BY DATETIME DESC LIMIT 1;')
					DBrow = DBcursor.fetchone()
					
					# make a tweet about the TEMP_DHT
					if (DBrow is not None):
						RAIN_value = DBrow[6]
						if (RAIN_value >= RAIN_THRESHOLD):
							RAIN_TEXT = RAIN_TEXT_YES
						else:
							RAIN_TEXT = RAIN_TEXT_NO
						tweetText = "@" + twitter_mention_user_screen_name + ", " + random.choice(RAIN_TWEETS).format(RAIN_TEXT)
						try:
							twitter.update_status(status=tweetText, in_reply_to_status_id=twitter_mention_id)
							LOG(LOG_INF,"Twitted succesfully: \"{}\"".format(tweetText), logPreLn=True)
						except TwythonError as e:
							LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e), logPreLn=True)
		
				# MENTIONS: PHOTO
				elif (("photo" in twitter_mention_text_last_lower) or ("picture" in twitter_mention_text_last_lower) or ("image" in twitter_mention_text_last_lower) or ("foto" in twitter_mention_text_last_lower)):
					
					# get file and script names
					ipCamFileName = ipCamFileNameDef.format(nowDatetime('%Y%m%d_%H%M%S'))
					ipCamFileNameFull = ipCamPathFull + '/' + ipCamFileName
					ipCamScript = ipCamScriptDef.format(ipCamFileName)
					
					# call to the process to get the image from the ip cam
					subprocess.call(ipCamScript, shell=True)
					
					# get the image ready for the tweet
					# https://twython.readthedocs.io/en/latest/usage/advanced_usage.html#updating-status-with-image
					photo = Image.open(ipCamFileNameFull)
					# ipCam lies on its left side: rotate 90 (anti-clockwise / to the left)
					photo = photo.rotate(90)
					# basewidth = 320
					# wpercent = (basewidth / float(photo.size[0]))
					# height = int((float(photo.size[1]) * float(wpercent)))
					# photo = photo.resize((basewidth, height), Image.ANTIALIAS)
					image_io = StringIO()
					photo.save(image_io, format='JPEG')
					image_io.seek(0)
					response = twitter.upload_media(media=image_io)
					
					# make a tweet about the photo
					tweetText = "@" + twitter_mention_user_screen_name + ", " + "this is a live picture of myself!"
					try:
						twitter.update_status(status=tweetText, in_reply_to_status_id=twitter_mention_id, media_ids=[response['media_id']])
						LOG(LOG_INF,"Twitted succesfully: \"{}\"".format(tweetText), logPreLn=True)
					except TwythonError as e:
						LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e), logPreLn=True)
		
				# MENTIONS: ELSE
				else: 
					tweetText = "@" + twitter_mention_user_screen_name + ", " + random.choice(DEFAULT_TWEETS)
					try:
						twitter.update_status(status=tweetText, in_reply_to_status_id=twitter_mention_id)
						LOG(LOG_INF,"Twitted succesfully: \"{}\"".format(tweetText), logPreLn=True)
					except TwythonError as e:
						LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e), logPreLn=True)
		
		# AUTO TWEETS MANAGEMENT
		
		# TEMP_DHT management
		if (timer_tweet_TEMP_DHT.isReady()):
		
			# get last TEMP_DHT temperature from DB
			DBcursor.execute('SELECT * FROM WEATHER WHERE WPAR=\'TEMP\' AND WPARID=\'DHT\' ORDER BY DATETIME DESC LIMIT 1;')
			DBrow = DBcursor.fetchone()
			
			# make a tweet about the TEMP_DHT
			if (DBrow is not None):
				TEMP_DHT_value = DBrow[6]
				tweetText = random.choice(TEMP_TWEETS).format(TEMP_DHT_value)
				try:
					twitter.update_status(status=tweetText)
					LOG(LOG_INF,"Twitted succesfully: \"{}\"".format(tweetText), logPreLn=True)
				except TwythonError as e:
					LOG(LOG_ERR,"<<< ERROR: TwythonError: \"{}\" >>>".format(e), logPreLn=True)
			else:
				LOG(LOG_WAR,"<<< WARNING: No rows found in DB (txTwitterActionManager, WEATHER) >>>", logPreLn=True)
			

