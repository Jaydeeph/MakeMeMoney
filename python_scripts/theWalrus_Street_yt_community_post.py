#!/usr/bin/env python3
# Copyright (C) 2020 Jaydeep

import time
from notifiers import get_notifier
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
pushbullet = get_notifier('pushbullet')

previous_message = ''
while True:
    driver = webdriver.Firefox(options=options)
    driver.get('https://www.youtube.com/c/theWalrusStreet/community')
    assert "theWalrus Street - YouTube" in driver.title

    yt_author_post_time = driver.find_element_by_id('header-author')
    yt_content = driver.find_element_by_id('content-text')

    print(yt_content.text)

    if('minutes ago' in yt_author_post_time.text and yt_content.text != previous_message):
        previous_message = yt_content.text
        pushbullet.notify( message='\'theWalrus Street\' made a new community post! \n https://www.youtube.com/c/theWalrusStreet/community', token='', title='theWalrus Street', type_='note', device_iden='')
    else:
        print('No new update')
    
    driver.quit()
    time.sleep(600)