# -*- coding: utf-8 -*-
import os

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

    def __init__(self, user='', start='', end='', save_html=False, *args, **kwargs):
        super(UserDataByPeriod, self).__init__(*args, **kwargs)
        self.user_name = user
        self.date_start = start
        self.date_end = end
        self.save_html = save_html
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
        percentage = ex.xpath('tr/td/span[contains(concat(" ", @class, " "), "efint ")][2]/text()')

        return zip(load, reps, sets, percentage )

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

    def parse_to_file(self, response):
        file_dir = 'data/' + self.user_name + '/pages/'
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        filename = file_dir + str(self.date) + '.html'

        with open(filename, 'wb') as html_file:
            html_file.write(response.body)
            html_file.close()

    def recursive_parse(self, response):
        """
           Parse training data
        """
        body_weight = response.xpath('//span[@class="weight bwnum weightunit-1"]/text()').extract()
        jbody = response.xpath('//div[@id="jbody"]')
        if body_weight:
            if self.save_html:
                self.parse_to_file(response)

            items = []
            for  comment, eblock in zip(jbody.xpath('div[@class="userText"]'), jbody.xpath('div[@class="eblock"]')):
                """ Each # Exercise """

                item = WeightxrepsItem()
                item['user_name'] = self.user_name
                item['exercise_date'] = response.url[-10:]
                item['user_weight'] = body_weight
                item['exercise_name'] = eblock.xpath('div/strong/span[@class="ename"]/text()').extract()
                item['max_weight'] = eblock.xpath('table[@class="sha stats"]/tbody/tr/td/a/span[@kg][1]/text()').extract()[1]

                for ex in eblock.xpath('table[@class=""]/tbody'):
                    """ Exercise table"""
                    zipped_data = self.extract_exercise(ex)
                    for load, reps, sets, percentage in zipped_data:
                        amount_of_sets = self.extract_sets(sets)
                        for _ in range(int(amount_of_sets[0])):
                            i = item.copy()
                            i['exercise_load'] = load.extract()
                            i['repetitions_done'] = reps.extract()
                            i['intensity'] = percentage.extract()
                            if i['intensity'] == 'PR':
                                i['intensity'] = 100
                            items.append(i)

            self.items.extend(items)

        if self.date < self.date_end:  # Add a day and continue scraping
            self.date += timedelta(days=1)
            return Request(self.start_urls[0] + str(self.date), self.recursive_parse)

        return self.items
