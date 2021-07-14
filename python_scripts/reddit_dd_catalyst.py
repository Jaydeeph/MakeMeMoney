#!/usr/bin/env python3
# Copyright (C) 2021 Jaydeep


from collections import Counter
from datetime import datetime, timedelta
from timeit import default_timer as timer
from psaw import PushshiftAPI
from tabulate import tabulate
from pprint import pprint

SUBREDDIT_DICTIONARY = {'pennystocks':'Penny Stocks',
                        'wallstreetbets':'Wall Street Bets',
                        'smallstreetbets':'Small Street Bets',
                        'stocks':'Stocks',
                        'SPACs' : 'SPACS',
                        'investing' : 'Investing' }

save_to_html = True
push_shift_api = PushshiftAPI()

def get_reddit_submission_data(subreddit, epoch_before_time, epoch_after_time, filter):
    searched_submissions = list(push_shift_api.search_submissions(after = epoch_after_time, before = epoch_before_time, subreddit = subreddit, filter = filter))
    return searched_submissions

def get_dd_catalyst_posts(subreddit_posts, subreddit_name):
    search_query = ['DD', 'CATALYST', 'TECHNICAL ANALYSIS', 'STOCK INFO', 'DD/RESEARCH', 'EPIC DD ANALYSIS', 'FUNDAMENTALS/DD', 'COMPANY NEWS', 'COMPANY ANALYSIS', 'DEFINITIVE AGREEMENT', 'NEW SPAC']
    dd_posts = []
    catalyst_posts = []
    other_valid_posts = []
    all_posts = {}

    for post in subreddit_posts:
        if hasattr(post, 'selftext'):
            if ('[removed]' in post.selftext):
                continue

        for query in search_query:
            if 'TheDailyDD' in subreddit_name or 'MillennialBets' in subreddit_name:
                dd_posts.append(post.url)
                continue
            if hasattr(post, 'link_flair_text'):
                if query in post.link_flair_text.upper():
                    if ('reddit.com' in post.url):
                        if ('DD' in query):
                            dd_posts.append(post.url)
                            continue
                        elif ('CATALYST' in query):
                            catalyst_posts.append(post.url)
                            continue
                        else:
                            other_valid_posts.append(post.url)
                            continue

    if bool(dd_posts):
        all_posts['Due Dilligences'] = dd_posts
    
    if bool(catalyst_posts):
        all_posts['Catalysts'] = catalyst_posts

    if bool(other_valid_posts):
        all_posts['Others'] = other_valid_posts

    if bool(all_posts):
        return all_posts
    else:
        return []

def print_dd(subreddit_key, individual_subreddits):
    header = ['Due Dilligences', 'Catalysts', 'Others']
    tabulate(individual_subreddits, headers=header)

def save_dd_to_html(subreddit_key, valid_posts):
    header = ['Due Dilligences', 'Catalysts', 'Others']
    file = open(subreddit_key + '_dd.html', 'w')
    file.write(tabulate(valid_posts, tablefmt='html', headers=header))
    file.close()

if __name__ == '__main__':
    start = timer()
    individual_subreddits = dict()

    datetime_24_hours_ago = datetime.today() - timedelta(hours = 24)
    timestamp_24_hour_ago = int(datetime_24_hours_ago.timestamp())
    timestamp_now = int(datetime.today().timestamp())
    filter = ['title', 'link_flair_text', 'selftext', 'url']

    for subreddit_key in SUBREDDIT_DICTIONARY.keys():
        subreddit_posts = get_reddit_submission_data(subreddit_key, timestamp_now, timestamp_24_hour_ago, filter)
        valid_posts = get_dd_catalyst_posts(subreddit_posts, subreddit_key)

        if bool(valid_posts):
            if (save_to_html):
                save_dd_to_html(subreddit_key, valid_posts)
            else:
                individual_subreddits[subreddit_key] = valid_posts