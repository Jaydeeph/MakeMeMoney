#!/usr/bin/env python3
# Copyright (C) 2020 Jaydeep

import argparse
import math
import os
import re
import sys
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import pandas

table_row_width = 10
web_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
          'Upgrade-Insecure-Requests': '1', 'Cookie': 'v2=1495343816.182.19.234.142', 'Accept-Encoding': 'gzip, deflate, sdch'}
TABLE_HEADER_LIST = ['Ticker', 'Company', 'Sector', 'Industry', 'Country', 'Market Cap', 'P/E', 'Price' ,'Change', 'Volume']

JAY_CUSTOM_SCANNER = 'https://finviz.com/screener.ashx?v=111&f=sh_curvol_o20000,sh_price_u5,ta_change_u2,ta_changeopen_u2,ta_perf_1wup,ta_perf2_dup&ft=4&o=-change'
HIGH_VOLUME_POSITIVE_MOVEMENT_SCANNER = 'https://finviz.com/screener.ashx?v=111&f=an_recom_holdbetter,fa_pb_u5,fa_quickratio_o1,sh_curvol_o1000,sh_float_u100,sh_price_u7,sh_relvol_o1.5,ta_sma20_pa20&ft=4&o=ticker'
SHORT_SQUEEZE = 'https://finviz.com/screener.ashx?v=131&f=sh_avgvol_o100,sh_instown_u50,sh_price_o2,sh_short_o15&ft=4&o=-shortinterestshare'
WEEKLY_EARNING_GAP_UP = 'https://finviz.com/screener.ashx?v=141&f=earningsdate_tomorrowafter,sh_avgvol_o400,sh_curvol_o50,sh_short_u25,ta_averagetruerange_o0.5,ta_gap_u2&ft=4&o=-perfytd'
BANKRUPTCY_SQUEEZE_CANDIDATES = 'https://finviz.com/screener.ashx?v=131&f=fa_pb_low,sh_short_o30&ft=4&o=-shortinterestshare'
POTENTIAL_UPTREND_FROM_WEEKLY_LOWS = 'https://finviz.com/screener.ashx?v=141&f=sh_avgvol_o400,ta_pattern_channelup,ta_perf_1wdown&ft=4&o=perf1w'
BOUNCE_AT_MOVING_AVERAGE = 'https://finviz.com/screener.ashx?v=141&f=sh_avgvol_o400,sh_curvol_o2000,sh_relvol_o1,ta_sma20_pa,ta_sma50_pb&ft=4&o=-perf1w'
OVERSOLD_REVERSAL = 'https://finviz.com/screener.ashx?v=111&f=sh_price_o5,sh_relvol_o2,ta_change_u,ta_rsi_os30&ft=4&o=price'
OVERSOLD_WITH_UPCOMING_EARNINGS = 'https://finviz.com/screener.ashx?v=141&f=cap_smallover,earningsdate_thismonth,fa_epsqoq_o15,fa_grossmargin_o20,sh_avgvol_o750,sh_curvol_o1000,ta_perf_52w10o,ta_rsi_nob50&ft=4&o=perfytd'
BREAKING_OUT = 'https://finviz.com/screener.ashx?v=141&f=fa_debteq_u1,fa_roe_o20,sh_avgvol_o100,ta_highlow50d_nh,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4&o=-perf1w'
HIGH_EARNINGS_GROWTH = 'https://finviz.com/screener.ashx?v=141&f=fa_epsqoq_o25,fa_epsyoy_o25,fa_epsyoy1_o25,fa_salesqoq_o25,sh_avgvol_o400,ta_rsi_nos50,ta_sma200_pa&ft=4&o=-perfytd'
HIGH_RELATIVE_VOLUME = 'https://finviz.com/screener.ashx?v=131&f=fa_curratio_o1,fa_epsqoq_o15,fa_quickratio_o1,fa_salesqoq_o15,sh_avgvol_o400,sh_price_o5,sh_relvol_o1.5,ta_sma20_pa,ta_sma200_sb50,ta_sma50_sa200&ft=4&o=instown'
CONSISTENT_GROWTH_ON_BULLISH_TREND = 'https://finviz.com/screener.ashx?v=141&f=fa_eps5years_pos,fa_epsqoq_o20,fa_epsyoy_o25,fa_epsyoy1_o15,fa_estltgrowth_pos,fa_roe_o15,sh_instown_o10,sh_price_o15,ta_highlow52w_a90h,ta_rsi_nos50&ft=4&o=-perfytd'
BUY_AND_HOLD_VALUE = 'https://finviz.com/screener.ashx?v=121&f=cap_microover,fa_curratio_o1.5,fa_estltgrowth_o10,fa_peg_o1,fa_roe_o15,ta_beta_o1.5,ta_sma20_pa&ft=4&o=-forwardpe'
UNDERVALUED_DIVIDEND_GROWTH = 'https://finviz.com/screener.ashx?v=111&f=cap_largeover,fa_div_pos,fa_epsyoy1_o5,fa_estltgrowth_o5,fa_payoutratio_u50,fa_pe_u20,fa_peg_low&ft=4&o=-pe'
LOW_PE_VALUE = 'https://finviz.com/screener.ashx?v=141&f=cap_smallunder,fa_pb_low,fa_pe_low,fa_peg_low,fa_roa_pos,fa_roe_pos,sh_price_o5&ft=4&o=-perfytd'
CANSLIM = 'https://finviz.com/screener.ashx?v=111&f=fa_eps5years_o20,fa_epsqoq_o20,fa_epsyoy_o20,fa_sales5years_o20,fa_salesqoq_o20,sh_curvol_o200&ft=4'


def get_table_results(soup):
    finviz_screener_td_results = soup.find_all(lambda tag: tag.name == 'td', class_ = 'screener-body-table-nw')

    finviz_screener_results = []
    count = 1
    for i in range(len(finviz_screener_td_results)):
        if(count == 1):
            count += 1
            continue

        a_text = finviz_screener_td_results[i].find_all('a')
        finviz_screener_results += [x.text for x in a_text]

        count += 1
        if(count == 12):
            count = 1

    return finviz_screener_results


def convert_table_results(finviz_screener_results):
    w, h = table_row_width, int(round(len(finviz_screener_results) / table_row_width))
    finviz_screener_data = [[0 for x in range(w)] for y in range(h)]

    x, y, = 0, 0
    for i in finviz_screener_results:
        if(i == ''):
            finviz_screener_data[x][y] = '-'
        else:
            finviz_screener_data[x][y] = i

        if(y == 9):
            y = 0
            x += 1
        else:
            y += 1

    return finviz_screener_data



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Finviz Insider Trades', description='Scrape Finviz Screener Data.')
    parser.add_argument('--jcs', default=False, action='store_true', help='JAY_CUSTOM_SCANNER')
    parser.add_argument('--hvpm', default=False, action='store_true', help='HIGH_VOLUME_POSITIVE_MOVEMENT_SCANNER')
    parser.add_argument('--ss', default=False, action='store_true', help='SHORT_SQUEEZE')
    parser.add_argument('--wegu', default=False, action='store_true', help='WEEKLY_EARNING_GAP_UP')
    parser.add_argument('--bsc', default=False, action='store_true', help='BANKRUPTCY_SQUEEZE_CANDIDATES')
    parser.add_argument('--pufwl', default=False, action='store_true', help='POTENTIAL_UPTREND_FROM_WEEKLY_LOWS')
    parser.add_argument('--bama', default=False, action='store_true', help='BOUNCE_AT_MOVING_AVERAGE')
    parser.add_argument('--osr', default=False, action='store_true', help='OVERSOLD_REVERSAL')
    parser.add_argument('--owue', default=False, action='store_true', help='OVERSOLD_WITH_UPCOMING_EARNINGS')
    parser.add_argument('--bo', default=False, action='store_true', help='BREAKING_OUT')
    parser.add_argument('--heg', default=False, action='store_true', help='HIGH_EARNINGS_GROWTH')
    parser.add_argument('--hrv', default=False, action='store_true', help='HIGH_RELATIVE_VOLUME')
    parser.add_argument('--cgobt', default=False, action='store_true', help='CONSISTENT_GROWTH_ON_BULLISH_TREND')
    parser.add_argument('--bahv', default=False, action='store_true', help='BUY_AND_HOLD_VALUE')
    parser.add_argument('--udg', default=False, action='store_true', help='UNDERVALUED_DIVIDEND_GROWTH')
    parser.add_argument('--lpev', default=False, action='store_true', help='LOW_PE_VALUE')
    parser.add_argument('--canslim', default=False, action='store_true', help='CANSLIM (William ONeil)')

    args = parser.parse_args()

    request = ''

    if(args.jcs):
        print('Getting JAY_CUSTOM_SCANNER')
        request = requests.get(JAY_CUSTOM_SCANNER, headers=web_headers)
    elif(args.hvpm):
        print('Getting HIGH_VOLUME_POSITIVE_MOVEMENT_SCANNER')
        request = requests.get(HIGH_VOLUME_POSITIVE_MOVEMENT_SCANNER, headers=web_headers)
    elif(args.ss):
        print('Getting SHORT_SQUEEZE')
        request = requests.get(SHORT_SQUEEZE, headers=web_headers)
    elif(args.wegu):
        print('Getting WEEKLY_EARNING_GAP_UP')
        request = requests.get(WEEKLY_EARNING_GAP_UP, headers=web_headers)
    elif(args.bsc):
        print('Getting BANKRUPTCY_SQUEEZE_CANDIDATES')
        request = requests.get(BANKRUPTCY_SQUEEZE_CANDIDATES, headers=web_headers)
    elif(args.pufwl):
        print('Getting POTENTIAL_UPTREND_FROM_WEEKLY_LOWS')
        request = requests.get(POTENTIAL_UPTREND_FROM_WEEKLY_LOWS, headers=web_headers)
    elif(args.bama):
        print('Getting BOUNCE_AT_MOVING_AVERAGE')
        request = requests.get(BOUNCE_AT_MOVING_AVERAGE, headers=web_headers)
    elif(args.osr):
        print('Getting OVERSOLD_REVERSAL')
        request = requests.get(OVERSOLD_REVERSAL, headers=web_headers)
    elif(args.owue):
        print('Getting OVERSOLD_WITH_UPCOMING_EARNINGS')
        request = requests.get(OVERSOLD_WITH_UPCOMING_EARNINGS, headers=web_headers)
    elif(args.bo):
        print('Getting BREAKING_OUT')
        request = requests.get(BREAKING_OUT, headers=web_headers)
    elif(args.heg):
        print('Getting HIGH_EARNINGS_GROWTH')
        request = requests.get(HIGH_EARNINGS_GROWTH, headers=web_headers)
    elif(args.hrv):
        print('Getting HIGH_RELATIVE_VOLUME')
        request = requests.get(HIGH_RELATIVE_VOLUME, headers=web_headers)
    elif(args.cgobt):
        print('Getting CONSISTENT_GROWTH_ON_BULLISH_TREND')
        request = requests.get(CONSISTENT_GROWTH_ON_BULLISH_TREND, headers=web_headers)
    elif(args.bahv):
        print('Getting BUY_AND_HOLD_VALUE')
        request = requests.get(BUY_AND_HOLD_VALUE, headers=web_headers)
    elif(args.udg):
        print('Getting UNDERVALUED_DIVIDEND_GROWTH')
        request = requests.get(UNDERVALUED_DIVIDEND_GROWTH, headers=web_headers)
    elif(args.lpev):
        print('Getting LOW_PE_VALUE')
        request = requests.get(LOW_PE_VALUE, headers=web_headers)
    elif(args.canslim):
        print('Getting CANSLIM')
        request = requests.get(CANSLIM, headers=web_headers)
    else:
        print('Error, please select from a valid argument. Use "-h" for more information.')
        exit(1)

    soup = BeautifulSoup(request.content, 'html.parser')
    finviz_screener_results = get_table_results(soup)
    finviz_screener_data = convert_table_results(finviz_screener_results)