from config_bot import *
import praw
import traceback
import ConfigParser
import ast
import time
import urllib
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout
import pdb
import re
import os
import requests
from experiment import generate10haikus
DO_SUBMISSIONS = False
DO_COMMENTS = True
MAXPOSTS = 100

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

inspi = ["summer","winter","autumn","love","lust","sex","success",'frog','moon','city','life']

def parse(comment):
    theme = comment.split(" ")
    if len(theme) ==2:
        return theme[1]
    else:
        return "random"

inspiration = "random"  

def check_condition(c):
    global inspiration
    text = c.body
    tokens = text.lower().split()
    inspiration = parse(text)
    if ('gimmehaiku' in tokens):
        return True



def bot_action(c,f,posts_replied_to):
    message = generate10haikus(inspiration)
    if(len(message)==0) or inspiration=="random":
      inspiration = inspi[random.randint(0,11)]
      message = generate10haikus(inspiration)
    while True:
        try:           
            c.reply(message)
            print("replied!!")
            # write these out as we go so if we get rate limited, we have the data 
            f.write(c.id + "\n")

            # Store the current id into our list
            posts_replied_to.append(c.id)
            break
        except praw.errors.RateLimitExceeded as error:
            #print '\tSleeping for %d seconds' % error.sleep_time
            time.sleep(error.sleep_time)
'''
def replybot(r,SUBREDDIT):
    #all comments that have already been replied to
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt", "r+") as f:
           posts_replied_to = f.read()

    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt", "r+") as f:
           #print("2")
           posts_replied_to = f.read()
           posts_replied_to = posts_replied_to.split("\n")
           posts_replied_to = filter(None, posts_replied_to)
        print('Searching %s.' % SUBREDDIT)
        subreddit = r.get_subreddit(SUBREDDIT)
        posts = []
        if DO_SUBMISSIONS:
            posts += list(subreddit.get_new(limit=MAXPOSTS))
        if DO_COMMENTS:
            posts += list(subreddit.get_comments(limit=MAXPOSTS))
        posts.sort(key=lambda x: x.created_utc)
        print("1")
        for post in posts:
            # Anything that needs to happen every loop goes here.
            print(post.body)

            pid = post.id
            if check_condition(post): 
                print("3")
                try:
                    pauthor = post.author.name
                except AttributeError:
                    # Author is deleted. We don't care about this post.
                    continue

                if pauthor.lower() == r.user.name.lower():
                    # Don't reply to yourself, robot!
                    print('Will not reply to myself.')
                    continue

                if pid in posts_replied_to:
                    # Post is already in the database
                    continue

                print('Replying to %s by %s' % (pid, pauthor))
                try:
                    bot_action(post,f,posts_replied_to)
                except praw.errors.Forbidden:
                    print('403 FORBIDDEN - is the bot banned from %s?' % post.subreddit.display_name)
'''

def run_main_reddit_loop(r,subreddit):
    #print("1")
    #all comments that have already been replied to
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt", "r+") as f:
           posts_replied_to = f.read()

    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt", "r+") as f:
           #print("2")
           posts_replied_to = f.read()
           posts_replied_to = posts_replied_to.split("\n")
           posts_replied_to = filter(None, posts_replied_to)

           #print("3")
           #Main loop the listens to new comments on some subreddit
             for c in praw.helpers.comment_stream(r, subreddit):
                 already_commented = False
                 #print("4")
                 if check_condition(c):
                     #print(c.body) 
                     if c.id not in posts_replied_to:
                         submission = r.get_submission(submission_id=c.permalink)
                         flat_comments = praw.helpers.flatten_tree(submission.comments)
                         already_commented = False
                         for comment in flat_comments:
                            ''' if str(comment.author) == USERNAME:
                                 #print "Bot replying to : ", comment.body
                                 # write these out as we go so if we get rate limited, we have the data 
                                 f.write(comment.id + "\n")
                       
                                 # Store the current id into our list
                                 posts_replied_to.append(comment.id)
                                 already_commented = True
                                 break'''
                            if not already_commented:
                                 bot_action(c,f,posts_replied_to)


# =============================================================================
# RUNNER
# =============================================================================

if __name__ == '__main__':
    BOT_START_TIME = int(time.time())
    while True:
        try:
            #print("Retrieving OAuth token...")
            replybot(get_praw(),"all")
        except praw.errors.OAuthInvalidToken:
            print("OAuth token expired.")
        except praw.errors.HTTPException:
            print("HTTP error. Retrying in 10...")
            time.sleep(10)