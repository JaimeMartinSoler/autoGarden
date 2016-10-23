#!/usr/bin/python

# imports
from twython import Twython, TwythonError
# import keys and tokens (file 'twitterPass.py' is ignored in .gitignore by GitHub)
from twitterPass import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET

# get twitter instance from keys and tokens
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# make a tweet
tweetText = 'Hello from Twython 5!'
try:
    twitter.update_status(status=tweetText)
except TwythonError as e:
    print (e)
	