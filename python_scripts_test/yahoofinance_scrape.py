#!/usr/bin/env python3
# Copyright (C) 2020 Jaydeep

import requests
from bs4 import BeautifulSoup
from pprint import pprint
web_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', 'Upgrade-Insecure-Requests': '1', 'Cookie': 'v2=1495343816.182.19.234.142', 'Accept-Encoding': 'gzip, deflate, sdch'}

ticker = 'AAPL'
ticker_details = dict()

yahoo_summary = 'https://finance.yahoo.com/quote/TICKER?p=TICKER'.replace('TICKER', ticker)
yahoo_summary_request = requests.get(yahoo_summary, headers=web_headers)
yahoo_summary_soup = BeautifulSoup(yahoo_summary_request.content, 'html.parser')

ticker_details['Current Price'] = yahoo_summary_soup.select('span[class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]')[0].text
ticker_details['Previous Close'] = yahoo_summary_soup.select('td[data-test="PREV_CLOSE-value"]')[0].span.text
ticker_details['Open'] = yahoo_summary_soup.select('td[data-test="OPEN-value"]')[0].span.text
ticker_details['Days Range'] = yahoo_summary_soup.select('td[data-test="DAYS_RANGE-value"]')[0].text
ticker_details['52 Weeks Range'] = yahoo_summary_soup.select('td[data-test="FIFTY_TWO_WK_RANGE-value"]')[0].text
ticker_details['Volume'] = yahoo_summary_soup.select('td[data-test="TD_VOLUME-value"]')[0].span.text
ticker_details['Avg Volume'] = yahoo_summary_soup.select('td[data-test="AVERAGE_VOLUME_3MONTH-value"]')[0].span.text
ticker_details['Market Cap'] = yahoo_summary_soup.select('td[data-test="MARKET_CAP-value"]')[0].span.text
ticker_details['Beta (5Y Monthly)'] = yahoo_summary_soup.select('td[data-test="BETA_5Y-value"]')[0].span.text
ticker_details['PE Ratio (TTM)'] = yahoo_summary_soup.select('td[data-test="PE_RATIO-value"]')[0].span.text
ticker_details['EPS (TTM)'] = yahoo_summary_soup.select('td[data-test="EPS_RATIO-value"]')[0].span.text
ticker_details['Earnings Date'] = yahoo_summary_soup.select('td[data-test="EARNINGS_DATE-value"]')[0].span.text
ticker_details['Forward Dividend & Yield'] = yahoo_summary_soup.select('td[data-test="DIVIDEND_AND_YIELD-value"]')[0].text
ticker_details['Ex-Dividend Date'] = yahoo_summary_soup.select('td[data-test="EX_DIVIDEND_DATE-value"]')[0].span.text
ticker_details['1y Target Est'] = yahoo_summary_soup.select('td[data-test="ONE_YEAR_TARGET_PRICE-value"]')[0].span.text

pprint(ticker_details)
