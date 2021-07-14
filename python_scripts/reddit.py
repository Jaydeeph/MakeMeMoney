#!/usr/bin/env python3
# Copyright (C) 2020 Jaydeep

import argparse
import math
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from timeit import default_timer as timer

import pandas
from psaw import PushshiftAPI
from requests.api import head
from tabulate import tabulate
from yahooquery import Ticker

BASE_POINTS = 4
BONUS_POINTS = 2
UPVOTE_FACTOR = 2
TOTAL_POINTS_THRESHOLD = 15
TABLE_HEADER = ['Ticker', 'Total Points', '24H Points', '48H Points', '% Change', '# DD\'s/Catalyst', 'Total Rockets']
YAHOO_TABLE_HEADER_API = ['Ticker', 'CurrentPrice', 'TargetLowPrice', 'TargetMedianPrice', 'TargetHighPrice', 'Recommendation', 'MarketVolume', 'MarketCap', 'InsiderPercentage']
YAHOO_TABLE_HEADER_SCRAPE = ['Ticker', 'Current Price', 'Previous Close', '52 Week Range', 'Average Volume', 'Volume', 'Earnings Date']
SUBREDDIT_DICTIONARY = { 'pennystocks':'Penny Stocks', 'RobinHoodPennyStocks':'RobinHood Penny Stocks', 'wallstreetbets':'Wall Street Bets', 'smallstreetbets':'Small Street Bets', 'StockMarket':'Stock Market', 'stocks':'Stocks' }
push_shift_api = PushshiftAPI()

def get_reddit_submission_data(subreddit, epoch_before_time, epoch_after_time, filter):
    searched_submissions = list(push_shift_api.search_submissions(after = epoch_after_time, before = epoch_before_time, subreddit = subreddit, filter = filter))
    return searched_submissions

def analyse_subreddit_data(subreddit_posts):
    regex_pattern = '[A-Z]{3,5}'
    ticker_points = dict()
    ticker_rockets = dict()
    ticker_dd_catalyst = dict()
    ticker_posts = dict()
    BANNED_WORDS = [
        'ADS', 'AKA', 'AMTES', 'BOOM', 'BUY', 'CBS', 'CDT', 'CEO', 'COVID', 'ELI', 
        'ETF', 'FDA', 'FOMO', 'FOR', 'FUCK', 'GROUP', 'HIGH', 'HOLD', 'HOT', 'IMO', 
        'ING', 'MAYBE', 'MERGE', 'MONDA', 'MOON', 'NEWS', 'NOW', 'OTC', 'OVER', 'PPP', 
        'REIT', 'ROPE', 'SEC', 'SELL', 'SHIT', 'SSR', 'SUPPO', 'THANK', 'THE', 'THIS', 
        'TLDR', 'USA', 'USD', 'WARNI', 'WILL', 'WSB', 'YOU'
    ]

    def is_ticker_valid(ticker):
        ticker_details = Ticker(ticker, validate=True)
        if(ticker in ticker_details.symbols):
            return True
        else:
            return False

    def collect_information(ticker, post, total_points, has_dd_or_catalyst):
        if ticker in ticker_points:
            ticker_points[ticker] += total_points
        else:
            ticker_points[ticker] = total_points

        if ticker in ticker_posts:
            ticker_posts[ticker].append(post.url)
        else:
            ticker_posts[ticker] = [post.url]

        if has_dd_or_catalyst:
            if ticker in ticker_dd_catalyst:
                ticker_dd_catalyst[ticker] += 1
            else:
                ticker_dd_catalyst[ticker] = 1
                
        if '🚀' in post.title:
            if ticker in ticker_rockets:
                ticker_rockets[ticker] += post.title.count('🚀')
            else:
                ticker_rockets[ticker] = post.title.count('🚀')

    for post in subreddit_posts:
        total_points = BASE_POINTS
        has_dd_or_catalyst = False
        if hasattr(post, 'link_flair_text'):
            if 'DD' in post.link_flair_text.upper():
                total_points += BONUS_POINTS
                has_dd_or_catalyst = True
            if 'CATALYST' in post.link_flair_text.upper():
                total_points += BONUS_POINTS
                has_dd_or_catalyst = True
            if 'DD/RESEARCH' in post.link_flair_text.upper():
                total_points += BONUS_POINTS
                has_dd_or_catalyst = True
            if 'EPIC DD ANALYSIS' in post.link_flair_text.upper():
                total_points += BONUS_POINTS
                has_dd_or_catalyst = True

        if hasattr(post, 'score') and UPVOTE_FACTOR > 0:
            total_points += math.ceil(post.score/UPVOTE_FACTOR)

        if hasattr(post, 'title'):
            title_extracted = set(re.findall(regex_pattern, post.title))
            for ticker in title_extracted:
                if(ticker in BANNED_WORDS): continue
                if(not is_ticker_valid(ticker)): continue
                collect_information(ticker, post, total_points, has_dd_or_catalyst)

        if len(title_extracted) > 0:
            continue

        if hasattr(post, 'selftext'):
            selftext_extracted = set(re.findall(regex_pattern, post.selftext))
            for ticker in selftext_extracted:
                if(ticker in BANNED_WORDS): continue
                if(not is_ticker_valid(ticker)): continue
                collect_information(ticker, post, total_points, has_dd_or_catalyst)

    return ticker_points, ticker_rockets, ticker_dd_catalyst, ticker_posts


def filter_high_scored_tickers(ticker_points):
    # filtered_ticker_points = dict(filter(lambda ticker_point: ticker_point[1] > TOTAL_POINTS_THRESHOLD, ticker_points.items())) # TypeError: 'list' object is not callable
    filtered_ticker_points = {key: value for (key, value) in ticker_points.items() if value >= TOTAL_POINTS_THRESHOLD}
    filtered_sorted_ticker_points = dict(sorted(filtered_ticker_points.items(), key=lambda item: item[1], reverse=True))
    return filtered_sorted_ticker_points


def filter_data_and_get_statistics(ticker_points_24h, ticker_points_48h,ticker_dd_catalyst_24h, ticker_dd_catalyst_48h, ticker_rockets_24h, ticker_rockets_48h, ticker_reddit_posts_24h, ticker_reddit_posts_48h):
    total_points = dict()
    total_filtered_dd_catalyst = dict()
    total_filtered_rockets = dict()
    percentage_change = dict()
    #total_filtered_reddit_posts = dict()

    total_points = merge_dictionary_sets(ticker_points_24h, ticker_points_48h)
    total_dd_catalyst = merge_dictionary_sets(ticker_dd_catalyst_24h, ticker_dd_catalyst_48h)
    total_rockets = merge_dictionary_sets(ticker_rockets_24h, ticker_rockets_48h)
    #total_reddit_posts = merge_dictionary_sets(ticker_reddit_posts_24h, ticker_reddit_posts_48h)

    for ticker in total_points:
        total_filtered_dd_catalyst[ticker] = total_dd_catalyst[ticker]
        total_filtered_rockets[ticker] = total_rockets[ticker]
        #total_filtered_reddit_posts[ticker] = total_reddit_posts[ticker]
    
    for ticker in total_points:
        if ticker in ticker_points_24h and ticker in ticker_points_48h:
            increase = ticker_points_24h[ticker] - ticker_points_48h[ticker]
            percentage_increase = (increase / ticker_points_48h[ticker]) * 100
            percentage_change[ticker] = str(round(percentage_increase, 3)) + '%'
        else:
            percentage_change[ticker] = '0%'

    return total_points, total_filtered_dd_catalyst, total_filtered_rockets, percentage_change#, total_reddit_posts

def merge_dictionary_sets(dictionary_a, dictionary_b):
    A = Counter(dictionary_a)
    B = Counter(dictionary_b)
    return A + B


def merge_all_data(total_points, filtered_ticker_points_24h, filtered_ticker_points_48h, percentage_change, total_filtered_dd_catalyst, total_filtered_rockets):
    w, h, = 7, int(round(len(total_points)))
    final_table = [[0 for x in range(w)] for y in range(h)]

    x = 0
    for key, value in total_points.items():
        final_table[x][0] = key
        final_table[x][1] = value

        if key in filtered_ticker_points_24h:
            final_table[x][2] = filtered_ticker_points_24h[key]
        else:
            final_table[x][2] = 0

        if key in filtered_ticker_points_48h:
            final_table[x][3] = filtered_ticker_points_48h[key]
        else:
            final_table[x][3] = 0
        
        if key in percentage_change:
            final_table[x][4] = percentage_change[key]
        else:
            final_table[x][4] = 0

        if key in total_filtered_dd_catalyst:
            final_table[x][5] = total_filtered_dd_catalyst[key]
        else:
            final_table[x][5] = 0

        if key in total_filtered_rockets:
            final_table[x][6] = total_filtered_rockets[key]
        else:
            final_table[x][6] = 0

        x += 1

    return final_table

def get_yahoo_finance_details_api(tickers):
    w, h = 9, int(round(len(tickers)))
    ticker_yahoo_finance = [[0 for x in range(w)] for y in range(h)]

    x = 0
    for ticker in tickers:
        print(ticker)
        ticker_details = Ticker(ticker, formatted=True)

        ticker_yahoo_finance[x][0] = ticker
        if 'currentPrice' in ticker_details.financial_data[ticker]:
            if 'fmt' in ticker_details.financial_data[ticker]['currentPrice']:
                ticker_yahoo_finance[x][1] = ticker_details.financial_data[ticker]['currentPrice']['fmt']

        if 'targetLowPrice' in ticker_details.financial_data[ticker]:
            if 'fmt' in ticker_details.financial_data[ticker]['targetLowPrice']:
                ticker_yahoo_finance[x][2] = ticker_details.financial_data[ticker]['targetLowPrice']['fmt']

        if 'targetMedianPrice' in ticker_details.financial_data[ticker]:
            if 'fmt' in ticker_details.financial_data[ticker]['targetMedianPrice']:
                ticker_yahoo_finance[x][3] = ticker_details.financial_data[ticker]['targetMedianPrice']['fmt']

        if 'targetHighPrice' in ticker_details.financial_data[ticker]:
            if 'fmt' in ticker_details.financial_data[ticker]['targetHighPrice']:
                ticker_yahoo_finance[x][4] = ticker_details.financial_data[ticker]['targetHighPrice']['fmt']

        if 'recommendationKey' in ticker_details.financial_data[ticker]:
            ticker_yahoo_finance[x][5] = ticker_details.financial_data[ticker]['recommendationKey']

        if 'regularMarketVolume' in ticker_details.price[ticker]:
            if (isinstance(ticker_details.price[ticker]['regularMarketVolume'], int)):
                ticker_yahoo_finance[x][6] = ticker_details.price[ticker]['regularMarketVolume']
            else:
                if 'fmt' in ticker_details.price[ticker]['regularMarketVolume']:
                    ticker_yahoo_finance[x][6] = ticker_details.price[ticker]['regularMarketVolume']['fmt']

        if 'marketCap' in ticker_details.price[ticker]:
            if 'fmt' in ticker_details.price[ticker]['marketCap']:
                ticker_yahoo_finance[x][7] = ticker_details.price[ticker]['marketCap']['fmt']

        if 'heldPercentInsiders' in ticker_details.key_stats[ticker]:
            if 'fmt' in ticker_details.key_stats[ticker]['heldPercentInsiders']:
                ticker_yahoo_finance[x][8] = ticker_details.key_stats[ticker]['heldPercentInsiders']['fmt']

        x += 1

    return ticker_yahoo_finance

def get_yahoo_finance_details_scrape(tickers):
    w, h = 6, int(round(len(tickers)))
    ticker_yahoo_finance = [[0 for x in range(w)] for y in range(h)]

    x = 0
    for ticker in tickers:
        web_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', 'Upgrade-Insecure-Requests': '1', 'Cookie': 'v2=1495343816.182.19.234.142', 'Accept-Encoding': 'gzip, deflate, sdch'}
        yahoo_summary = 'https://finance.yahoo.com/quote/TICKER?p=TICKER'.replace('TICKER', ticker)
        yahoo_summary_request = requests.get(yahoo_summary, headers=web_headers)
        yahoo_summary_soup = BeautifulSoup(yahoo_summary_request.content, 'html.parser')
        
        ticker_yahoo_finance[x][0] = yahoo_summary_soup.select('span[class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]')[0].text
        ticker_yahoo_finance[x][1] = yahoo_summary_soup.select('td[data-test="PREV_CLOSE-value"]')[0].span.text
        ticker_yahoo_finance[x][2] = yahoo_summary_soup.select('td[data-test="FIFTY_TWO_WK_RANGE-value"]')[0].text
        ticker_yahoo_finance[x][3] = yahoo_summary_soup.select('td[data-test="AVERAGE_VOLUME_3MONTH-value"]')[0].span.text
        ticker_yahoo_finance[x][4] = yahoo_summary_soup.select('td[data-test="TD_VOLUME-value"]')[0].span.text
        ticker_yahoo_finance[x][5] = yahoo_summary_soup.select('td[data-test="EARNINGS_DATE-value"]')[0].span.text
        
        x += 1

    return ticker_yahoo_finance

def print_results(sorted_final_table, tickers_yahoo_finance):
    print(tabulate(sorted_final_table, headers=TABLE_HEADER))
    print(tabulate(tickers_yahoo_finance, headers=YAHOO_TABLE_HEADER_API))

def save_results_to_html(subreddit_key, sorted_final_table):
    file = open(subreddit_key + '_points.html', 'w')
    file.write(tabulate(sorted_final_table, tablefmt='html', headers=TABLE_HEADER))
    file.close()

def save_yahoo_to_html(subreddit_key, tickers_yahoo_finance):
    file = open(subreddit_key + '_points_yahoo.html', 'w')
    file.write(tabulate(tickers_yahoo_finance, tablefmt='html', headers=YAHOO_TABLE_HEADER_SCRAPE))
    file.close()

if __name__ == '__main__':
    start = timer()
    individual_subreddits = dict()

    datetime_24_hours_ago = datetime.today() - timedelta(hours = 24)
    timestamp_24_hour_ago = int(datetime_24_hours_ago.timestamp())
    timestamp_48_hours_ago = int((datetime_24_hours_ago - timedelta(hours = 24)).timestamp())
    timestamp_now = int(datetime.today().timestamp())
    filter = ['title', 'link_flair_text', 'selftext', 'score', 'url']

    for subreddit_key in SUBREDDIT_DICTIONARY.keys():
        print(subreddit_key)

        # Get 24 hours posts. And 48 hours posts.
        subreddit_posts_24h = get_reddit_submission_data(subreddit_key, timestamp_now, timestamp_24_hour_ago, filter)
        subreddit_posts_48h = get_reddit_submission_data(subreddit_key, timestamp_24_hour_ago, timestamp_48_hours_ago, filter)
        
        # Gets total points, number of rockets in posts, if dd/catalyst points. For both 24 hours and 48 hours.
        ticker_points_24h, ticker_rockets_24h, ticker_dd_catalyst_24h, ticker_reddit_posts_24h = analyse_subreddit_data(subreddit_posts_24h)
        ticker_points_48h, ticker_rockets_48h, ticker_dd_catalyst_48h, ticker_reddit_posts_48h = analyse_subreddit_data(subreddit_posts_48h)

        # Filter through the data to only keep high scored results.
        filtered_ticker_points_24h = filter_high_scored_tickers(ticker_points_24h)
        filtered_ticker_points_48h = filter_high_scored_tickers(ticker_points_48h)

        # Merge the ticker data and get statistics on the differences.
        total_points, total_filtered_dd_catalyst, total_filtered_rockets, percentage_change = filter_data_and_get_statistics(filtered_ticker_points_24h, filtered_ticker_points_48h,ticker_dd_catalyst_24h, ticker_dd_catalyst_48h, ticker_rockets_24h, ticker_rockets_48h, ticker_reddit_posts_24h, ticker_reddit_posts_48h)

        # Get ticker details from yahoo.
        tickers_yahoo_finance = get_yahoo_finance_details_api(total_points.keys())
        # tickers_yahoo_finance = get_yahoo_finance_details_scrape(total_points.keys())

        # Merge all the data so its easy to tabulate. And then sort it from the highest points.
        final_table = merge_all_data(total_points, filtered_ticker_points_24h, filtered_ticker_points_48h, percentage_change, total_filtered_dd_catalyst, total_filtered_rockets)
        sorted_final_table = sorted(final_table, key=lambda x: x[1], reverse=True)

        save_results_to_html(subreddit_key, sorted_final_table)
        save_yahoo_to_html(subreddit_key, tickers_yahoo_finance)

    elapsed_time = timer() - start
    print('Took ' + str(elapsed_time / 60000) + ' mins.')
