#!/usr/bin/env python3
# Copyright (C) 2021 Jaydeep

import math
import re
import requests
import logging

from datetime import datetime, timedelta
from psaw import PushshiftAPI
from tabulate import tabulate
from yahooquery import Ticker
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


web_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', 'Upgrade-Insecure-Requests': '1', 'Cookie': 'v2=1495343816.182.19.234.142', 'Accept-Encoding': 'gzip, deflate, sdch'}

# Points Variables
BASE_POINTS = 4
BONUS_POINTS = 2
UPVOTE_FACTOR = 2
COMMENT_FACTOR = 2
TOTAL_POINTS_THRESHOLD = 15

TABLE_HEADER = [
    'Tickers', 'Points', 'Total Upvotes', 'Total Comments', 'Awards List'
]

# Subreddits to scan
SUBREDDIT_DICTIONARY = {
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

# Currently using selenium and its super slow for such tasks.
# With new pushshift API, update the following:
# Get actual score, rather then delayed data.
# Get awards and give points based on awards.
def analyse_subreddit_data(subreddit_key, subreddit_posts):
    logging.info('Analysing subreddit data')

    # This is a regex match to get anything that may be a ticker.
    regex_pattern = '[A-Z]{3,5}'

    # List of DD/Catalyst flairs to validate against.
    DD_CATALYST_FLAIRS = [
        'IN-DEPTH RESEARCH', 'BREAKING NEWS', 'GOOD NEWS',
        'BREAKOUT STOCK ALERT', 'MERGER - R/S - OFFERING ALERT', 'DD',
        'CATALYST', 'TECHNICAL ANALYSIS', 'BULLISH', 'STOCK INFO',
        'DD/RESEARCH', 'EPIC DD ANALYSIS', 'FUNDAMENTALS/DD', 'COMPANY NEWS',
        'COMPANY ANALYSIS', 'DEFINITIVE AGREEMENT'
    ]

    # Words to ignore, as regex check doesn't aquire actual tickers.
    IGNORE_WORDS = [
        'BUY', 'CEO', 'COVID', 'ELI', 'ETF', 'FDA', 'FOMO', 'FOR', 'FUCK',
        'GROUP', 'HIGH', 'HOLD', 'HOT', 'IMO', 'MAYBE', 'MERGE', 'NEWS', 'NOW',
        'OTC', 'OVER', 'SEC', 'SELL', 'SHIT', 'THANK', 'THE', 'THIS', 'TLDR',
        'USA', 'USD', 'WARNI', 'WILL', 'WSB', 'YOU', 'YOLO'
    ]

    ticker_points = dict()
    ticker_awards = dict()
    ticker_number_of_awards = dict()
    ticker_number_of_upvotes = dict()
    dd_catalyst_posts = dict()

    options = Options()
    options.headless = True
    options.add_argument('log-level=3')

    DRIVER_PATH = 'C:\Dev\chromedriver'
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.set_window_size(1920, 1080)

    # Check
    def is_post_valid(url):
        if 'reddit.com' in url:
            if 'reddit.com/gallery' in url or 'redd.it' in url:
                return False
            else:
                return True

    def get_tickers_from_text(valid_tickers, text):
        tickers_extracted = re.findall(regex_pattern, text)
        for ticker in tickers_extracted:
            if ticker not in IGNORE_WORDS and ticker not in valid_tickers:
                if is_ticker_valid(ticker):
                    valid_tickers.append(ticker)
        return valid_tickers

    def is_ticker_valid(ticker):
        ticker_details = Ticker(ticker, validate=True)
        if ticker in ticker_details.symbols:
            return True
        else:
            return False

    def get_flair_list(flairs):
        flair_list = []
        for flair in post_flairs:
            flair_list.append(flair.get_text(strip=True))
        return flair_list

    def is_dd_catalyst_in_flairs(flair_list):
        for flair in flair_list:
            if flair in DD_CATALYST_FLAIRS:
                return True
        return False

    def get_number_from_text(number_text):
        if 'Vote' in number_text: return 0
        if 'k' in number_text:
            if '.' in number_text:
                score_part_1 = int(number_text.split('.')[0]) * 1000
                score_part_2 = int(number_text.split('.')[1].split('k')[0]) * 100
                return int(score_part_1 + score_part_2)
            else:
                return int(number_text.split('k')[0]) * 1000
        else:
            return int(number_text)

    def get_award_details(awards):
        number_of_awards = 0
        awards_list = []
        for award in awards:
            image = award.find('img')
            number_of_award_given = award.find_all('span')[1].get_text(strip=True)
            award_name = image.get('alt', '')
            awards_list.append(award_name)
            if number_of_award_given != '':
                number_of_awards = int(number_of_award_given)
        return number_of_awards, awards_list

    for post in subreddit_posts:
        if not is_post_valid(post.url): continue

        print(post.url)
        driver.get(post.url)
        page_source = driver.page_source
        post_soup = BeautifulSoup(page_source, 'html.parser')
        post_content = post_soup.select('div[data-test-id="post-content"]')
        if (not post_content): continue
        post_content = post_content[0]

        try:
            post_title = post_content.select('h1[class="_eYtD2XCVieq6emjKBH3m"]')[0].get_text(strip=True)
            post_body = post_content.select('div[class="_292iotee39Lmt0MkQZ2hPV RichTextJSON-root"]')[0].get_text(strip=True)
            post_no_upvotes = post_content.select('div[class="_1rZYMD_4xY3gRcSS3p8ODO _3a2ZHWaih05DgAOtvu6cIo"]')[0].get_text(strip=True)
            post_no_comments = post_content.select('span[class="FHCV02u6Cp2zYL0fhQPsO"]')[0].text.split(' ')[0]
            post_flairs = post_content.select('div[class="lrzZ8b0L6AzLkQj5Ww7H1"]')[1].find_all('span')
            post_awards = post_content.select('span[class="_2OYwDdghtXEuTF67C95YLY"]')

            valid_tickers = []
            total_points = BASE_POINTS

            valid_tickers = get_tickers_from_text(valid_tickers, post_title)
            valid_tickers = get_tickers_from_text(valid_tickers, post_body)

            number_of_upvotes = get_number_from_text(post_no_upvotes)
            number_of_comments = get_number_from_text(post_no_comments)

            if number_of_upvotes > 2:
                total_points += math.ceil(number_of_upvotes / UPVOTE_FACTOR)

            if number_of_comments > 2:
                total_points += math.ceil(number_of_comments / COMMENT_FACTOR)

            flair_list = get_flair_list(post_flairs)
            contains_dd_catalyst = is_dd_catalyst_in_flairs(flair_list)

            number_of_awards, awards_list = get_award_details(post_awards)
            total_points += number_of_awards

            if contains_dd_catalyst:
                formatted_url = '<a href="{url}"\>{title}\</a>'.format(url=post.url, title=post_title)
                if subreddit_key in dd_catalyst_posts:
                    dd_catalyst_posts[subreddit_key].append(formatted_url)
                else:
                    dd_catalyst_posts[subreddit_key] = [formatted_url]

            for ticker in valid_tickers:
                if ticker in ticker_points:
                    ticker_points[ticker] += total_points
                else:
                    ticker_points[ticker] = total_points

                if ticker in ticker_number_of_awards:
                    ticker_number_of_awards[ticker] += number_of_awards
                else:
                    ticker_number_of_awards[ticker] = number_of_awards

                if ticker in ticker_number_of_upvotes:
                    ticker_number_of_upvotes[ticker] += number_of_upvotes
                else:
                    ticker_number_of_upvotes[ticker] = number_of_upvotes

                for award in awards_list:
                    if ticker in ticker_awards:
                        if award not in ticker_awards[ticker]:
                            ticker_awards[ticker].append(award)
                    else:
                        ticker_awards[ticker] = [award]

        except IndexError:
            try:
                deleted_post = post_content.select('div[class="_2jpm-rNr0Hniw6BX3NWMVe"]')[0].get_text(strip=True)
                print(deleted_post)
                continue
            except Exception:
                print('Exceptional exception occurred.')
                continue

    return ticker_points, ticker_number_of_upvotes, ticker_number_of_awards, ticker_awards, dd_catalyst_posts

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

def merge_data(filtered_sorted_ticker_points, ticker_number_of_upvotes, ticker_number_of_awards, ticker_awards):
    w, h, = 5, int(round(len(filtered_sorted_ticker_points)))
    final_table = [[0 for x in range(w)] for y in range(h)]

    y = 0
    for ticker in filtered_sorted_ticker_points:
        url = 'https://finance.yahoo.com/quote/TICKER'.replace('TICKER', ticker)
        ticker_url = '<a href="{url}">{ticker}</a>'.format(url=url, ticker=ticker)

        final_table[y][0] = ticker_url
        final_table[y][1] = filtered_sorted_ticker_points[ticker]

        if ticker in ticker_number_of_upvotes:
            final_table[y][2] = ticker_number_of_upvotes[ticker]
        else:
            final_table[y][2] = 0

        if ticker in ticker_number_of_awards:
            final_table[y][3] = ticker_number_of_awards[ticker]
        else:
            final_table[y][3] = 0

        if ticker in ticker_awards:
            final_table[y][4] = ticker_awards[ticker]
        else:
            final_table[y][4] = 0

        y += 1

    return final_table


def save_data_to_html(subreddit_key, final_table, dd_catalyst_posts):
    
    file = open(subreddit_key + '_points.html','w')
    file.write(
        tabulate(final_table,
                 tablefmt='html',
                 headers=TABLE_HEADER))
    file.close()

    file = open(subreddit_key + '_dd.html', 'w')
    file.write(
        tabulate(dd_catalyst_posts,
                 tablefmt='html',
                 headers=['Reddit Posts URL']))
    file.close()


def save_urls(subreddit_posts):
    file = open('reddit_saved_urls.txt', 'w')
    for post in subreddit_posts:
        file.write(post.url)
        file.write('\n')
    file.close()


if __name__ == '__main__':
    logging.info('Running All In One.')

    reddit_filter = ['url']
    datetime_24_hours_ago = datetime.today() - timedelta(hours=24)
    timestamp_24_hour_ago = int(datetime_24_hours_ago.timestamp())
    timestamp_now = int(datetime.today().timestamp())

    for subreddit_key in SUBREDDIT_DICTIONARY:

        subreddit_posts = get_reddit_submission_data(subreddit_key, timestamp_now,
                                                    timestamp_24_hour_ago,
                                                    reddit_filter)

        ticker_points, ticker_number_of_upvotes, ticker_number_of_awards, ticker_awards, dd_catalyst_posts = analyse_subreddit_data(
            subreddit_key, subreddit_posts)

        filtered_sorted_ticker_points = filter_high_scored_tickers(ticker_points)

        final_table = merge_data(filtered_sorted_ticker_points,
                                ticker_number_of_upvotes,
                                ticker_number_of_awards,
                                ticker_awards)

        print('filtered_sorted_ticker_points')
        print(filtered_sorted_ticker_points)
        print('\n')
        print('ticker_number_of_upvotes')
        print(ticker_number_of_upvotes)
        print('\n')
        print('ticker_number_of_awards')
        print(ticker_number_of_awards)
        print('\n')
        print('ticker_awards')
        print(ticker_awards)
        print('\n')
        print('dd_catalyst_posts')
        print(dd_catalyst_posts)
        print('\n')
        print(tabulate(dd_catalyst_posts, headers=['Reddit Posts URL']))

        print(tabulate(final_table, headers=TABLE_HEADER))
        print(tabulate(dd_catalyst_posts, headers=['Reddit Posts URL']))
        save_data_to_html(subreddit_key, final_table, dd_catalyst_posts)
        break