#!/usr/bin/env python3
# Copyright (C) 2020 Jaydeep

from logging import log
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# options = Options()
# options.headless = True

username = ''
password = ''
yahoo_login_link = 'https://login.yahoo.com/'
yahoo_profile_link = 'https://finance.yahoo.com/portfolios'
webull_account_link = ''

def store_cookies(driver):
    cookies = driver.get_cookies()
    for cookie in cookies:
        with open('cookies.txt', 'a') as stored_cookies:
            stored_cookies.write(str(cookie) + '\n')

def restore_cookies(driver):
    with open('cookies.txt') as stored_cookies:
        cookie = eval(stored_cookies.readline())
        driver.add_cookie(cookie)

def login_to_yahoo(driver):
    driver.get(yahoo_login_link)
    time.sleep(5)
    restore_cookies(driver)

    driver.get(yahoo_login_link)

    if(not 'Jaydeep' in driver.page_source):
        assert 'Sign in' in driver.page_source

        username_input = driver.find_element_by_id('login-username')
        username_input.send_keys(username)

        next_button = driver.find_element_by_id('login-signin')
        next_button.send_keys(Keys.RETURN)

        password_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        password_input.send_keys(password)

        next_button = driver.find_element_by_id('login-signin')
        next_button.click()

        return True

def go_to_portfolio(driver):
    driver.get(yahoo_profile_link)
    t212_portfolio = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tr.Bgc\(\$hoverBgColor\)\:h:nth-child(3) > td:nth-child(1) > div:nth-child(2) > a:nth-child(1)')))
    t212_portfolio.click()
    
def add_ticker_to_portfolio(driver, ticker):
    add_symbol = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Bdrs\(3px\)')))
    add_symbol.click()

    add_symbol_field = driver.find_element_by_css_selector('input.Bdrs\(0\):nth-child(1)')
    add_symbol_field.send_keys(ticker)
    add_symbol_field.send_keys(Keys.ENTER)


if __name__ == '__main__':
    ticker = 'AAPL'

    driver = webdriver.Firefox()

    login_to_yahoo(driver)
    go_to_portfolio(driver)
    add_ticker_to_portfolio(driver, ticker)

    driver.quit()