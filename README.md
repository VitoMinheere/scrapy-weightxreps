# Scrapy WXR
Scrape training data from https://www.weightxreps.com

## Table of contents
* [General info](#general-info)
* * [Setup](#setup)
* * [Status](#status)
* * [Inspiration](#inspiration)

## General info
Weightxreps allows you to purchase your own data by donating $5. This is what i recommend when you are interested in your own training data. However i am also interested in training data from others.

## Setup
Create a new virtual environment and install the requirements with ```pip install -r requirements.txt```

## Code Examples
Show examples of usage:
```sh
	scrapy crawl weightxreps
  	-a user=[username]
    	-a start=[start date]
      	-a end=[end date]
        -o [where to save the output]
	-t [format of the result]
```

Date format is YYYY-MM-DD

```sh
# Data by date 2015-09-30
scrapy crawl weightxreps -a user='Bosshogg' -a start='2015-09-30' -a end='2015-09-30' -o /data/Bosshogg.csv -t csv

# Today's data
scrapy crawl weightxreps -a user='Bosshogg' -a start='today' -o /data/Bosshogg.csv -t csv
```

## Status
Project is: _in progress_, scraping is possible, however i am not getting all the data i want. I want to also add the user's comments

## Inspiration
Fork from https://github.com/linsdev/scrapy-weightxreps
