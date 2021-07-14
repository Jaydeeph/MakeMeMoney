#!/usr/bin/env python3
# Copyright (C) 2020 Jaydeep

import re
import math
from datetime import datetime, timedelta
from timeit import default_timer as timer
from psaw import PushshiftAPI
from yahooquery import Ticker
from tabulate import tabulate
from pprint import pprint

SUBREDDIT_DICTIONARY = {'pennystocks':'Penny Stocks',
                        'wallstreetbets':'Wall Street Bets',
                        'smallstreetbets':'Small Street Bets',
                        'stocks':'Stocks',
                        'investing' : 'Investing',
                        'SPACs' : 'SPACS', }

push_shift_api = PushshiftAPI()

def get_reddit_submission_data(subreddit, epoch_before_time, epoch_after_time, filter):
    searched_submissions = list(push_shift_api.search_submissions(after = epoch_after_time, before = epoch_before_time, subreddit = subreddit, filter = filter))
    return searched_submissions

def get_ticker_posts(ticker, subreddit_posts, subreddit_name):
    regex_pattern = '[A-Z]{3,5}'
    
    ticker_post_urls = dict()

    def add_post_urls(ticker, url):
        if ticker in ticker_post_urls:
            ticker_post_urls[ticker].append(url)
        else:
            ticker_post_urls[ticker] = [url]
    
    for post in subreddit_posts:
        ticker_found = False

        if hasattr(post, 'selftext'):
            if('removed' in post.selftext):
                continue

        if hasattr(post, 'title'):
            title_extracted = set(re.findall(regex_pattern, post.title))
            if(ticker in title_extracted):
                ticker_found = True
        
        if hasattr(post, 'selftext'):
            selftext_extracted = set(re.findall(regex_pattern, post.selftext))
            if(ticker in selftext_extracted):
                ticker_found = True
        
        if(not ticker_found):
            continue

        if ('reddit.com' in post.url):
            add_post_urls(ticker, post.url)

    if bool(ticker_post_urls):
        return ticker_post_urls
    else:
        return []

def get_dd_catalyst_sentiment(ticker):
    individual_subreddits = dict()
    datetime_48_hours_ago = datetime.today() - timedelta(hours = 48)
    timestamp_48_hour_ago = int(datetime_48_hours_ago.timestamp())
    timestamp_now = int(datetime.today().timestamp())
    filter = ['title', 'selftext', 'url']

    for subreddit_key in SUBREDDIT_DICTIONARY.keys():
        subreddit_posts = get_reddit_submission_data(subreddit_key, timestamp_now, timestamp_48_hour_ago, filter)
        valid_posts = get_ticker_posts(ticker, subreddit_posts, subreddit_key)

        if bool(valid_posts):
            individual_subreddits[subreddit_key] = valid_posts

    if bool(individual_subreddits):
        return individual_subreddits
    else:
        return 'No posts from this ticker found.'

if __name__ == '__main__':
    individual_subreddits = get_dd_catalyst_sentiment('ALPP')
    print(individual_subreddits)