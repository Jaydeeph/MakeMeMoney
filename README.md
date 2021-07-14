# Different python scripts do different things. Something I've been messing with throughout the pandemic.

# Scripts

## reddit.py
* Using PushshiftAPI, loops through the provided subreddits. Get the title, flair, body text, score, and URL of each post.
* Gets posts from the current time to 24 hours ago (let's call this new posts). Then gets posts from 24 hours ago to 48 hours ago (let's call this old posts). So 1-day differences.
* Now we analyse the data.
    * Now this is done for both new posts and old posts. 
    * We loop through the list of posts we received. Give the post an initial starter points. (I realised I should've validated the ticker first). 
    * Checks if the posts contain DD or Catalyst flair and give it extra points. 
    * Next adds points by dividing the post score by custom factor. 
    * Next if checks if the post has a title, if not it'll check the body text.
    * If the post contains text/body text, extracts ticker via regex pattern. Checks if the ticker is not in the banned words list. Checks if the ticker is valid using Yahoo API. 
    * Then collects information such as, total points, URL of the post, appends a point to the ticker if it contains dd/catalyst (ticker_dd_catalyst dictionary), and finally checks how many rockets the posts contain. (Maybe should add diamond hands too).
* Now that we have all this data, we filter the points by a threshold of our choosing. Here I chose a minimum point of 15 to be the threshold. Then sort it by the highest score value. 
* Next we merge the new posts with the old posts. And then filter out the other data to match the data (tickers) in total_points. Then get the percentage change in points in 24 hours.
* Next we get additional data using Yahoo API, such as current price, target price, recommendation, volume, and such.
* Then we merge all the data into one big multidimensional array. I just found this easier as I can convert this into an HTML table using tabulate. 

## finviz_custom_screener.py 
All this does is scrape the Finviz results from the custom screener, convert the data to the multidimensional array, (to do) then print the data using tabulate. Now each result from the custom screener gives different table sizes, so I need to modify my code to allow it to dynamically adjust accordingly. 

## finviz_insider_trading.py
Scrapes Finviz insider trading and displays the results in a table.

## online_portfolio_manager.py
Using selenium to log into yahoo finance and add the specific ticket into your portfolio. Tried to get it to add quantity/price too, however, the dynamic table made it difficult. 

## reddit_dd_catalyst.py
Goes through the provided subreddits, of 24 hours posts, checks if the posts flair matches the DD/Catalyst posts that I want, and keeps the URL to it. Provides a list of URLs. (No way to validate if the post was removed or not.)

## reddit_ticker_posts.py
Goes through the provided subreddits, of 48 hours posts, checks if the posts contain mentions of the ticker you are looking for. Provides a list of URLs.

## Website
This is something else that I've been testing instead of creating a flask project. Nothing interesting.

# To Do
* Make a scraper for Finviz.

# Disclaimer
I can't guarantee all these scrips will work correctly or as described. I have been working on these during my free time. I know some scripts just break suddenly if not maintained. Some things may be my fault, if so please do raise an issue. 