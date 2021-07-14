#!/usr/bin/env python3
# Copyright (C) 2021 Jaydeep

import math
import os
import re
import sys

from datetime import datetime, timedelta
from psaw import PushshiftAPI
from tabulate import tabulate
from yahooquery import Ticker
from bs4 import BeautifulSoup
import requests
import logging

web_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', 'Upgrade-Insecure-Requests': '1', 'Cookie': 'v2=1495343816.182.19.234.142', 'Accept-Encoding': 'gzip, deflate, sdch'}

# Points Variables
BASE_POINTS = 4
BONUS_POINTS = 2
UPVOTE_FACTOR = 2
COMMENT_FACTOR = 4
TOTAL_POINTS_THRESHOLD = 10

HEADER = [
    'TICKER',
    'POINTS'
]

# Subreddits to scan
SUBREDDIT_DICTIONARY = {
    'PennyStocksDD': 'Penny Stock DD',
    'pennystocks': 'Penny Stocks',
    'wallstreetbets': 'Wall Street Bets',
    'smallstreetbets': 'Small Street Bets',
    'StockMarket': 'Stock Market',
    'stocks': 'Stocks',
    'investing': 'Investing',
    'SPACs': 'SPACS'
}

push_shift_api = PushshiftAPI()


# Confugiring logging.
def configure_logging():
    logging.basicConfig(filename='all_in_one.log',
                        filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')


# Need to update it to new version of pushshift once its out of BETA.
def get_reddit_submission_data(subreddit, epoch_before_time, epoch_after_time,
                               reddit_filter):
    logging.info('Getting reddit submission data.')
    searched_submissions = list(
        push_shift_api.search_submissions(after=epoch_after_time,
                                          before=epoch_before_time,
                                          subreddit=subreddit,
                                          filter=reddit_filter))
    return searched_submissions


# With new pushshift API, update the following:
# Get actual score, rather then delayed data.
# Get awards and give points based on awards.
def analyse_subreddit_data(subreddit_posts):
    logging.info('Analysing subreddit data')
    regex_pattern = '[A-Z]{3,5}'
    flair_list = [
        'IN-DEPTH RESEARCH', 'BREAKING NEWS', 'GOOD NEWS',
        'BREAKOUT STOCK ALERT', 'MERGER - R/S - OFFERING ALERT', 'DD',
        'CATALYST', 'TECHNICAL ANALYSIS', 'BULLISH', 'STOCK INFO',
        'DD/RESEARCH', 'EPIC DD ANALYSIS', 'FUNDAMENTALS/DD', 'COMPANY NEWS',
        'COMPANY ANALYSIS', 'DEFINITIVE AGREEMENT'
    ]

    IGNORE_WORDS = [
        'BUY', 'CEO', 'COVID', 'ELI', 'ETF', 'FDA', 'FOMO', 'FOR', 'FUCK',
        'GROUP', 'HIGH', 'HOLD', 'HOT', 'IMO', 'MAYBE', 'MERGE', 'NEWS', 'NOW',
        'OTC', 'OVER', 'SEC', 'SELL', 'SHIT', 'THANK', 'THE', 'THIS', 'TLDR',
        'USA', 'USD', 'WARNI', 'WILL', 'WSB', 'YOU', 'YOLO'
    ]

    ticker_points = dict()
    dd_catalyst_posts = []

    def is_ticker_valid(ticker):
        ticker_details = Ticker(ticker, validate=True)
        if ticker in ticker_details.symbols:
            return True
        else:
            return False

    def is_post_valid(selftext):
        if 'removed' in selftext or 'deleted' in selftext:
            return True
        else:
            return False

    for post in subreddit_posts:
        if hasattr(post, 'selftext'):
            if not is_post_valid(post.selftext): continue

        valid_tickers = []
        total_points = BASE_POINTS

        if hasattr(post, 'title'):
            title_extracted = re.findall(regex_pattern, post.title)
            for ticker in title_extracted:
                if not is_ticker_valid(ticker):
                    continue
                else:
                    valid_tickers.append(ticker)

        if hasattr(post, 'selftext'):
            selftext_extracted = set(re.findall(regex_pattern, post.selftext))
            for ticker in selftext_extracted:
                if not is_ticker_valid(ticker):
                    continue
                else:
                    if ticker not in valid_tickers:
                        valid_tickers.append(ticker)

        if not valid_tickers: continue

        if hasattr(post, 'link_flair_text'):
            if post.link_flair_text.upper() in flair_list:
                total_points += BONUS_POINTS
                dd_catalyst_posts.append(
                    '<a href="{url}">{title}</a>'.format(url=post.url,
                                                         title=post.title))

        if hasattr(post, 'score') and UPVOTE_FACTOR > 0:
            total_points += math.ceil(post.score / UPVOTE_FACTOR)

        for ticker in valid_tickers:
            if ticker in ticker_points:
                ticker_points[ticker] += total_points
            else:
                ticker_points[ticker] = total_points

    return ticker_points, dd_catalyst_posts

def filter_high_scored_tickers(ticker_points):
    filtered_ticker_points = {
        key: value
        for (key, value) in ticker_points.items()
        if value >= TOTAL_POINTS_THRESHOLD
    }

    filtered_sorted_ticker_points = dict(
        sorted(filtered_ticker_points.items(),
               key=lambda item: item[1],
               reverse=True))

    return filtered_sorted_ticker_points

def save_urls(subreddit_posts):
    file = open('reddit_saved_urls.txt', 'w')
    for post in subreddit_posts:
        file.write(post.url)
        file.write('\n')
    file.close()


if __name__ == '__main__':
    logging.info('Running All In One.')

    reddit_filter = ['title', 'selftext', 'score', 'link_flair_text', 'url']
    datetime_24_hours_ago = datetime.today() - timedelta(hours=24)
    timestamp_24_hour_ago = int(datetime_24_hours_ago.timestamp())
    timestamp_now = int(datetime.today().timestamp())

    subreddit_posts = get_reddit_submission_data('wallstreetbets',
                                                 timestamp_now,
                                                 timestamp_24_hour_ago,
                                                 reddit_filter)

    ticker_points, dd_catalyst_posts = analyse_subreddit_data(subreddit_posts)
    filtered_sorted_ticker_points = filter_high_scored_tickers(ticker_points)

    print(tabulate(filtered_sorted_ticker_points))
    print(dd_catalyst_posts)