import praw
import pdb
import re
import os
import requests
import time
from config_bot import *
from experiment import generate10haikus

REDIRECT_URI = 'http://127.0.0.1:65010/authorize_callback'

AUTH_TOKENS = ["identity","history", "read", "modposts", "submit", "edit"]

def get_access_token():
    response = requests.post("https://www.reddit.com/api/v1/access_token",
      auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
      data = {"grant_type": "password", "username": USERNAME, "password": PASSWORD},
      headers = {"User-Agent": USER_AGENT})
    return dict(response.json())["access_token"]

def get_praw():
    r = praw.Reddit(USER_AGENT)
    r.set_oauth_app_info(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    r.set_access_credentials(set(AUTH_TOKENS), get_access_token())
    return r

def main(r):
	if not os.path.isfile("posts_replied_to.txt"):
	    posts_replied_to = []
	else:
	    with open("posts_replied_to.txt", "r") as f:
	       posts_replied_to = f.read()

	if not os.path.isfile("posts_replied_to.txt"):
	    posts_replied_to = []
	else:
	    with open("posts_replied_to.txt", "r") as f:
	       posts_replied_to = f.read()
	       posts_replied_to = posts_replied_to.split("\n")
	       posts_replied_to = filter(None, posts_replied_to)

	posts_replied_to = filter(None, posts_replied_to)

	
	subreddit = r.get_subreddit('lumos_haiku_test')

	f = open("posts_replied_to.txt","a")
	for submission in subreddit.get_hot(limit=50):
	    # print submission.title

	    # If we haven't replied to this post before
	    if submission.id not in posts_replied_to:

	        # Do a case insensitive search	
	        if re.search("hello world", submission.title, re.IGNORECASE):
	            # Reply to the post
	            try:
	            	
	                submission.add_comment(generate10haikus("food"))
	            except:
			print "Error: ", sys.exc_info()[0]
	                print "Probably rate limited cuz you're a bot."
	                f.close()
	                quit()
	            else:
	                print "Bot replying to : ", submission.title
	                # write these out as we go so if we get rate limited, we have the data 
	                f.write(submission.id + "\n")
	      
	                # Store the current id into our list
	                posts_replied_to.append(submission.id)

	# Close out the submissions replied to
	f.close()


if __name__ == "__main__":
    BOT_START_TIME = int(time.time())
    while True:
        try:
            print("Retrieving OAuth token...")
            main(get_praw())
        except praw.errors.OAuthInvalidToken:
            print("OAuth token expired.")
        except praw.errors.HTTPException:
            print("HTTP error. Retrying in 10...")
            time.sleep(10)