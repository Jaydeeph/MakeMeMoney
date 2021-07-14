#!/usr/bin/env python3
# Copyright (C) 2020 Jaydeep

import argparse
import math
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from pprint import pprint

web_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36', 'Upgrade-Insecure-Requests': '1', 'Cookie': 'v2=1495343816.182.19.234.142', 'Accept-Encoding': 'gzip, deflate, sdch'}

ticker_summary = dict()
ticker_statistics = dict()
ticker_history = []
ticker_profile = dict()
ticker_analysis = dict()
ticker_holders = dict()

def yahoo_summary_scrape(ticker):
    yahoo_summary = 'https://finance.yahoo.com/quote/TICKER?p=TICKER'.replace('TICKER', ticker)
    yahoo_summary_request = requests.get(yahoo_summary, headers=web_headers)
    yahoo_summary_soup = BeautifulSoup(yahoo_summary_request.content, 'html.parser')

    ticker_summary['Current Price'] = yahoo_summary_soup.select('span[class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]')[0].get_text()
    ticker_summary['After Hours Price'] = 'N/A' if not yahoo_summary_soup.select('span[class="C($primaryColor) Fz(24px) Fw(b)"]') else yahoo_summary_soup.select('span[class="C($primaryColor) Fz(24px) Fw(b)"]')[0].get_text()

    yahoo_summary_tables = yahoo_summary_soup.find_all("table")
    for table in yahoo_summary_tables:
        table_rows = table.find_all('tr')
        for table_row in table_rows:
            table_datas = table_row.find_all('td')
            ticker_summary[table_datas[0].get_text()] = table_datas[1].get_text()

    pprint(ticker_summary)

def yahoo_statistics_scrape(ticker):
    yahoo_statistics = 'https://finance.yahoo.com/quote/TICKER/key-statistics?p=TICKER'.replace('TICKER', ticker)
    yahoo_statistics_request = requests.get(yahoo_statistics, headers=web_headers)
    yahoo_statistics_soup = BeautifulSoup(yahoo_statistics_request.content, 'html.parser')

    yahoo_statistics_table = yahoo_statistics_soup.find_all("table")
    for table in yahoo_statistics_table:
        table_rows = table.find_all('tr')
        for table_row in table_rows:
            table_datas = table_row.find_all('td')
            ticker_statistics[table_datas[0].get_text()] = table_datas[1].get_text()

    pprint(ticker_statistics)

def yahoo_historic_scape(ticker):
    yahoo_historic = 'https://finance.yahoo.com/quote/TICKER/history?p=TICKER'.replace('TICKER', ticker)
    yahoo_historic_request = requests.get(yahoo_historic, headers=web_headers)
    yahoo_historic_soup = BeautifulSoup(yahoo_historic_request.content, 'html.parser')

    yahoo_historic_table = yahoo_historic_soup.find_all("tbody")
    for table in yahoo_historic_table:
        table_rows = table.find_all('tr')
        for table_row in table_rows:
            table_datas = table_row.find_all('td')
            if(len(table_datas) < 6):
                continue

            data = dict()
            data['Date'] = table_datas[0].get_text()
            data['Open'] = table_datas[1].get_text()
            data['High'] = table_datas[2].get_text()
            data['Low'] = table_datas[3].get_text()
            data['Close'] = table_datas[4].get_text()
            data['Adj Close'] = table_datas[5].get_text()
            data['Volume'] = table_datas[6].get_text()

            ticker_history.append(data)

    pprint(ticker_history)

def yahoo_profile_scrape(ticker):
    yahoo_profile = 'https://finance.yahoo.com/quote/TICKER/profile?p=TICKER'.replace('TICKER', ticker)
    yahoo_profile_request = requests.get(yahoo_profile, headers=web_headers)
    yahoo_profile_soup = BeautifulSoup(yahoo_profile_request.content, 'html.parser')

    asset_profile = yahoo_profile_soup.select('div[data-test="asset-profile"]')[0]
    ticker_profile['Company Name'] = asset_profile.select('h3')[0].get_text()
    ticker_profile['Sector(s)'] = asset_profile.select('span[class="Fw(600)"]')[0].get_text()
    ticker_profile['Industry'] = asset_profile.select('span[class="Fw(600)"]')[1].get_text()
    ticker_profile['Full Time Exployees'] = asset_profile.select('span[class="Fw(600)"]')[2].get_text()
    ticker_profile['Description'] = yahoo_profile_soup.select('p[class="Mt(15px) Lh(1.6)"]')[0].get_text()

    key_executive_table = yahoo_profile_soup.find_all("tbody")
    key_executives = []
    for table in key_executive_table:
        table_rows = table.find_all('tr')
        for table_row in table_rows:
            table_datas = table_row.find_all('td')

            key_executive = dict()
            key_executive['Name'] = table_datas[0].get_text()
            key_executive['Title'] = table_datas[1].get_text()
            key_executive['Pay'] = table_datas[2].get_text()
            key_executive['Exercised'] = table_datas[3].get_text()
            key_executive['Year Born'] = table_datas[4].get_text()

            key_executives.append(key_executive)

    ticker_profile['Key Executives'] = key_executives

    pprint(ticker_profile)

def yahoo_analysis_scrape(ticker):
    yahoo_analysis = 'https://finance.yahoo.com/quote/TICKER/analysis?p=TICKER'.replace('TICKER', ticker)
    yahoo_analysis_request = requests.get(yahoo_analysis, headers=web_headers)
    yahoo_analysis_soup = BeautifulSoup(yahoo_analysis_request.content, 'html.parser')

    analysis_tables = yahoo_analysis_soup.find_all("table")

    for table in analysis_tables:
        _list = []
        table_head = table.find_all('th')
        table_header_key = table_head[0].get_text()
        table_header_one = table_head[1].get_text()
        table_header_two = table_head[2].get_text()
        table_header_three = table_head[3].get_text()
        table_header_four = table_head[4].get_text()
        table_body = table.find_all('tbody')
        table_rows = table_body[0].find_all('tr')

        for table_row in table_rows:
            table_datas = table_row.find_all('td')
            temp_dict = dict()
            temp_dict['Key'] = table_datas[0].get_text()
            temp_dict[table_header_one] = table_datas[1].get_text()
            temp_dict[table_header_two] = table_datas[2].get_text()
            temp_dict[table_header_three] = table_datas[3].get_text()
            temp_dict[table_header_four] = table_datas[4].get_text()
            _list.append(temp_dict)
        
        ticker_analysis[table_header_key] = _list
    
    pprint(ticker_analysis)


def yahoo_holders_scrape(ticker):
    yahoo_holders = 'https://finance.yahoo.com/quote/TICKER/holders?p=TICKER'.replace('TICKER', ticker)
    yahoo_holders_request = requests.get(yahoo_holders, headers=web_headers)
    yahoo_holders_soup = BeautifulSoup(yahoo_holders_request.content, 'html.parser')

    holders_tables = yahoo_holders_soup.find_all('tbody')
    top_institutional_holders = holders_tables[1]
    top_mutual_fund_holders = holders_tables[2]

    top_institutional_holders_table_rows = top_institutional_holders.find_all('tr')
    top_institutional_holders_list = []
    for table_row in top_institutional_holders_table_rows:
        table_datas = table_row.find_all('td')
        top_institutional_holders_dict = dict()
        top_institutional_holders_dict['Holder'] = table_datas[0].get_text()
        top_institutional_holders_dict['Shares'] = table_datas[1].get_text()
        top_institutional_holders_dict['Date Reported'] = table_datas[2].get_text()
        top_institutional_holders_dict['% Out'] = table_datas[3].get_text()
        top_institutional_holders_dict['Value'] = table_datas[4].get_text()
        top_institutional_holders_list.append(top_institutional_holders_dict)

    ticker_holders['Top Institutional'] = top_institutional_holders_list

    top_mutual_fund_holders_table_rows = top_mutual_fund_holders.find_all('tr')
    top_mutual_fund_holders_list = []
    for table_row in top_mutual_fund_holders_table_rows:
        table_datas = table_row.find_all('td')
        top_mutual_fund_holders_dict = dict()
        top_mutual_fund_holders_dict['Holder'] = table_datas[0].get_text()
        top_mutual_fund_holders_dict['Shares'] = table_datas[1].get_text()
        top_mutual_fund_holders_dict['Date Reported'] = table_datas[2].get_text()
        top_mutual_fund_holders_dict['% Out'] = table_datas[3].get_text()
        top_mutual_fund_holders_dict['Value'] = table_datas[4].get_text()
        top_mutual_fund_holders_list.append(top_mutual_fund_holders_dict)

    ticker_holders['Top Mutual Fund'] = top_mutual_fund_holders_list


    yahoo_holders_insider = 'https://finance.yahoo.com/quote/TICKER/insider-roster?p=TICKER'.replace('TICKER', ticker)
    yahoo_holders_insider_request = requests.get(yahoo_holders_insider, headers=web_headers)
    yahoo_holders_insider_soup = BeautifulSoup(yahoo_holders_insider_request.content, 'html.parser')

    insider_roster_table_body = yahoo_holders_insider_soup.find_all('tbody')
    insider_roster_table_rows = insider_roster_table_body[0].find_all('tr')
    insider_roster_list = []
    for table_row in insider_roster_table_rows:
        table_datas = table_row.find_all('td')
        insider_roster_dict = dict()
        insider_roster_dict['Entity'] = table_datas[0].get_text()
        insider_roster_dict['Recent Transaction'] = table_datas[1].get_text()
        insider_roster_dict['Date'] = table_datas[2].get_text()
        insider_roster_dict['Total Shares Owned'] = table_datas[3].get_text()
        insider_roster_list.append(insider_roster_dict)

    ticker_holders['Insider Roster'] = insider_roster_list


    yahoo_insider_transactions = 'https://finance.yahoo.com/quote/TICKER/insider-transactions?p=TICKER'.replace('TICKER', ticker)
    yahoo_insider_transactions_request = requests.get(yahoo_insider_transactions, headers=web_headers)
    yahoo_insider_transactions_soup = BeautifulSoup(yahoo_insider_transactions_request.content, 'html.parser')

    insider_transactions_table_body = yahoo_insider_transactions_soup.find_all('tbody')
    
    insider_transactions_table_rows = insider_transactions_table_body[0].find_all('tr')
    insider_transactions_list = []
    for table_row in insider_transactions_table_rows:
        table_datas = table_row.find_all('td')
        insider_transactions_dict = dict()
        insider_transactions_dict['Key'] = table_datas[0].get_text()
        insider_transactions_dict['Shares'] = table_datas[1].get_text()
        insider_transactions_dict['Transactions'] = table_datas[2].get_text()
        insider_transactions_list.append(insider_transactions_dict)

    ticker_holders['6 Months Insider Transactions'] = insider_transactions_list

    insider_transactions_reported_table_rows = insider_transactions_table_body[2].find_all('tr')
    insider_transactions_reported_list = []
    for table_row in insider_transactions_reported_table_rows:
        table_datas = table_row.find_all('td')
        insider_transactions_reported_dict = dict()
        insider_transactions_reported_dict['Insider'] = table_datas[0].get_text()
        insider_transactions_reported_dict['Transaction'] = table_datas[1].get_text()
        insider_transactions_reported_dict['Type'] = table_datas[2].get_text()
        insider_transactions_reported_dict['Value'] = table_datas[3].get_text()
        insider_transactions_reported_dict['Date'] = table_datas[4].get_text()
        insider_transactions_reported_dict['Shares'] = table_datas[5].get_text()
        insider_transactions_reported_list.append(insider_transactions_reported_dict)

    ticker_holders['Insider Transactions Reported (2 Years)'] = insider_transactions_reported_list

    pprint(ticker_holders)

def get_yahoo_analysis(ticker):
    yahoo_analysis_scrape(ticker)

if __name__ == '__main__':
    ticker = 'AAPL'
    yahoo_analysis_scrape(ticker)