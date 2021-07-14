from bs4 import BeautifulSoup
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests


web_headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'Cookie': 'v2=1495343816.182.19.234.142',
    'Accept-Encoding': 'gzip, deflate, sdch'
}

urls = []
omg = 0
with open('reddit_saved_urls.txt') as opened_file:
    urls = opened_file.readlines()

DRIVER_PATH = 'C:\Dev\chromedriver'
options = Options()
options.headless = True
options.add_argument('log-level=3')
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

for url in urls:

    if 'reddit.com' not in url or 'reddit.com/gallery' in url: continue

    print(url)
    driver.get(url)

    page_source = driver.page_source
    # post_request = requests.get(reddit_url, headers=web_headers)
    post_soup = BeautifulSoup(page_source, 'html.parser')
    post = post_soup.select('div[data-test-id="post-content"]')[0]

    try:
        post_title = post.select('h1[class="_eYtD2XCVieq6emjKBH3m"]')[0].get_text(strip=True)
        post_body = post.select('div[class="_292iotee39Lmt0MkQZ2hPV RichTextJSON-root"]')[0].get_text(strip=True)
        post_no_upvotes = post.select('div[class="_1rZYMD_4xY3gRcSS3p8ODO _3a2ZHWaih05DgAOtvu6cIo"]')[0].get_text(strip=True)
        post_no_comments = post.select('span[class="FHCV02u6Cp2zYL0fhQPsO"]')[0].text.split(' ')[0]
        post_flairs = post.select('div[class="lrzZ8b0L6AzLkQj5Ww7H1"]')[1].find_all('span')
        post_awards = post.select('span[class="_2OYwDdghtXEuTF67C95YLY"]')
    except IndexError:
        deleted_post = post_soup.select(
            'div[class="_2jpm-rNr0Hniw6BX3NWMVe"]')[0].get_text(strip=True)
        print(deleted_post)
        continue
    except:
        driver.close()

    print(post_title)
    print(post_body)
    print(post_no_upvotes)
    if 'k' in post_no_upvotes:
        if '.' in post_no_upvotes:
            score_part_1 = int(post_no_upvotes.split('.')[0]) * 1000
            score_part_2 = int(post_no_upvotes.split('.')[1].split('k')[0]) * 100
            print(score_part_1 + score_part_2)
        else:
            score = int(post_no_upvotes.split('k')[0]) * 1000
            print(score)
    else:
        print(post_no_upvotes)

    print(post_no_comments)
    print(post_flairs)

    for flair in post_flairs:
        print(flair.get_text(strip=True))

    for award in post_awards:
        img = award.find('img')
        count = award.find_all('span')[1].get_text(strip=True)
        print(img.get('alt', ''))
        print(count) if count != '' else print('0')
        print('\n')

    if omg == 4: break
    omg += 1
