#!/usr/bin/env python3
# Copyright (C) 2020 Jaydeep

from yahooquery import Ticker
import os

os.system('cls')

ticker_name = 'fda'.upper()
ticker_details = dict()
custom_details = dict()

ticker_details = Ticker(ticker_name, validate=True, formatted=True)
print(ticker_details.symbols)

if(ticker_name in ticker_details.symbols):
    print('Valid Symbol')
else:
    print('Invalid Symbol')

print(ticker_details.price)

print('earningsDate ' + str(ticker_details.calendar_events[ticker_name]['earnings']['earningsDate'][0]))
print('dividendDate ' + str(ticker_details.calendar_events[ticker_name]['dividendDate']))


print('preMarketPrice ' + str(ticker_details.price[ticker_name]['preMarketPrice']))
print('postMarketChange ' + str(ticker_details.price[ticker_name]['postMarketChange']))
print('postMarketPrice ' + str(ticker_details.price[ticker_name]['postMarketPrice']))
print('regularMarketPrice ' + str(ticker_details.price[ticker_name]['regularMarketPrice']))
print('regularMarketDayHigh ' + str(ticker_details.price[ticker_name]['regularMarketDayHigh']))
print('regularMarketDayLow ' + str(ticker_details.price[ticker_name]['regularMarketDayLow']))
print('regularMarketVolume ' + str(ticker_details.price[ticker_name]['regularMarketVolume']))
print('longName ' + str(ticker_details.price[ticker_name]['longName']))
print('marketCap ' + str(ticker_details.price[ticker_name]['marketCap']))


print('heldPercentInsiders ' + str(ticker_details.key_stats[ticker_name]['heldPercentInsiders']))
print('heldPercentInstitutions ' + str(ticker_details.key_stats[ticker_name]['heldPercentInstitutions']))
print('lastSplitFactor ' + str(ticker_details.key_stats[ticker_name]['lastSplitFactor']))
print('lastSplitDate ' + str(ticker_details.key_stats[ticker_name]['lastSplitDate']))


print('currentPrice ' + str(ticker_details.financial_data[ticker_name]['currentPrice']))
print('targetHighPrice ' + str(ticker_details.financial_data[ticker_name]['targetHighPrice']))
print('targetLowPrice ' + str(ticker_details.financial_data[ticker_name]['targetLowPrice']))
print('targetMedianPrice ' + str(ticker_details.financial_data[ticker_name]['targetMedianPrice']))
print('recommendationKey ' + str(ticker_details.financial_data[ticker_name]['recommendationKey']))
