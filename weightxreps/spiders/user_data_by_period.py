# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from scrapy.spiders import CrawlSpider
from scrapy import Request
from weightxreps.items import WeightxrepsItem


class UserDataByPeriod(CrawlSpider):
    """
        Scrape an user's data by period.
        Either between predefined dates, today or the entire date range from user sign up
    """

    name = 'weightxreps'
    allowed_domains = ['weightxreps.net']

    def __init__(self, user='', start='', end='', *args, **kwargs):
        super(UserDataByPeriod, self).__init__(*args, **kwargs)
        self.user_name = user
        self.date_start = start
        self.date_end = end
        self.start_urls = ("http://weightxreps.net/journal/%s/" % user,)
        self.items = []
        self.date = None

    def extract_exercise(self, ex):
        """
            Extract the exercise data from the jbody text
        """
        load = ex.xpath('tr/td/span[@class="weight n W weightunit-1"]/text()')
        reps = ex.xpath('tr/td/span[@class="n R"]/text()')
        sets = ex.xpath('tr/td/span[@class="n"]/text()')
        return zip(load, reps, sets)

    def extract_sets(self, sets):
        items = sets.extract()
        cleaned_items = []
        for item in items:
            if item != '+':
                cleaned_items.append(item)
            else:
                # TODO add sets when BW+weight is used
                cleaned_items.append(1)

        return cleaned_items

    def parse(self, response):
        """
            Either scrape 1 day or the whole range from the day the user joined until today
        """
        if self.date_start == 'today':
            self.date_start = date.today()
        else:
            if not self.date_start:
                self.date_start = response.xpath('//strong[@id="joined"]/text()')[0].extract()
            self.date_start = datetime.strptime(self.date_start, '%Y-%m-%d').date()

        self.date_end = date.today() if self.date_end in ('today', '') else \
                        datetime.strptime(self.date_end, '%Y-%m-%d').date()

        self.date = self.date_start
        return Request(self.start_urls[0] + str(self.date), self.recursive_parse)

    def recursive_parse(self, response):
        """
            Scrape a specified range between dates
        """
        weight = response.xpath('//span[@class="weight bwnum weightunit-1"]/text()').extract()
        jbody = response.xpath('//div[@id="jbody"]')

        if weight:
            items = []
            for user_text, eblock in zip(jbody.xpath('div[@class="userText"]'),
                                         jbody.xpath('div[@class="eblock"]')):
                item = WeightxrepsItem()
                item['user_name'] = self.user_name
                item['exercise_date'] = response.url[-10:]
                item['user_weight'] = weight
                item['exercise_name'] = eblock.xpath('div/strong/span[@class="ename"]/text()').extract()
                #item['exercise_category'] = user_text.re(r'([a-zA-Z]+)<br>\s*<br>\s*</div>$') or \
                #                            items and items[-1]['exercise_category'] or None

                for ex in eblock.xpath('table[@class=""]/tbody'):
                    zipped_data = self.extract_exercise(ex)
                    for load, reps, sets in zipped_data:
                        amount_of_sets = self.extract_sets(sets)
                        print(amount_of_sets)
                        for _ in range(int(amount_of_sets[0])):
                            i = item.copy()
                            i['exercise_load'] = load.extract()
                            i['repetitions_done'] = reps.extract()
                            items.append(i)

            self.items.extend(items)

        if self.date < self.date_end:  # Add a day and continue scraping
            self.date += timedelta(days=1)
            return Request(self.start_urls[0] + str(self.date), self.recursive_parse)

        return self.items
