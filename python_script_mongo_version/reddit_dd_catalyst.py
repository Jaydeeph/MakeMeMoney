#!/usr/bin/env python3
# Copyright (C) 2020 Jaydeep

from datetime import datetime, timedelta
from timeit import default_timer as timer
from psaw import PushshiftAPI
import mongoengine as db
from pprint import pprint

SUBREDDIT_DICTIONARY = {'pennystocks':'Penny Stocks',
                        'RobinHoodPennyStocks':'RobinHood Penny Stocks',
                        'wallstreetbets':'Wall Street Bets',
                        'smallstreetbets':'Small Street Bets',
                        'stocks':'Stocks',
                        'SPACs' : 'SPACS',
                        'investing' : 'Investing' }

class Posts(db.Document):
    subreddit = db.StringField(required=True)
    post_type = db.StringField(required=True)
    post_link = db.StringField(required=True)
    date_time = db.DateTimeField(required=True)

push_shift_api = PushshiftAPI()

def connect_to_database():
    print('Connecting To Database...')
    db.connect('reddit_dd_catalyst', host='127.0.0.1', port=27017)
    print('Connected To Database.')

def get_reddit_submission_data(subreddit, epoch_before_time, epoch_after_time, filter):
    print('Searching Reddit...')

    searched_submissions = list(push_shift_api.search_submissions(after = epoch_after_time, before = epoch_before_time, subreddit = subreddit, filter = filter))
    return searched_submissions

def get_dd_catalyst_posts(subreddit_posts, subreddit_name):
    print('Sorting Data...')

    search_query = ['DD', 'CATALYST', 'TECHNICAL ANALYSIS', 'STOCK INFO', 'DD/RESEARCH', 'EPIC DD ANALYSIS', 'FUNDAMENTALS/DD', 'COMPANY NEWS', 'COMPANY ANALYSIS', 'DEFINITIVE AGREEMENT', 'NEW SPAC']
    for post in subreddit_posts:
        if hasattr(post, 'selftext'):
            if ('[removed]' in post.selftext):
                continue

        for query in search_query:
            if hasattr(post, 'link_flair_text'):
                if query in post.link_flair_text.upper():
                    if ('reddit.com' in post.url):
                        if ('DD' in query):
                            Posts(subreddit=subreddit_name, post_type="DD", post_link=post.url, date_time=datetime.now()).save()
                            continue
                        elif ('CATALYST' in query):
                            Posts(subreddit=subreddit_name, post_type="CATALYST", post_link=post.url, date_time=datetime.now()).save()
                            continue
                        else:
                            Posts(subreddit=subreddit_name, post_type="OTHER", post_link=post.url, date_time=datetime.now()).save()
                            continue


if __name__ == '__main__':
    connect_to_database()

    start = timer()
    individual_subreddits = dict()

    datetime_24_hours_ago = datetime.today() - timedelta(hours = 24)
    timestamp_24_hour_ago = int(datetime_24_hours_ago.timestamp())
    timestamp_now = int(datetime.today().timestamp())
    filter = ['title', 'link_flair_text', 'selftext', 'url']

    for subreddit_key in SUBREDDIT_DICTIONARY.keys():
        subreddit_posts = get_reddit_submission_data(subreddit_key, timestamp_now, timestamp_24_hour_ago, filter)
        get_dd_catalyst_posts(subreddit_posts, subreddit_key)
        break

    print('Finished.')