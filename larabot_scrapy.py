from scrapy import Spider
from scrapy.selector import Selector


class LaraBot(Spider):
    name = "lara_bot"
    start_urls = [
        'http://floripinhas.com.br/calendario/action~month/request_format~json/']

    months = ['janeiro', 'fevereiro', 'março', 'abril',
              'maio', 'junho', 'julho', 'agosto', 'setembro',
              'outubro', 'novembro', 'dezembro']

    def parse(self, response):

        days = []

        try:
            month, year = response.xpath(
                '//span[contains(@class, "ai1ec-calendar-title")]/text()').extract_first().split(' ')
        except:
            month = response.xpath(
                '//span[contains(@class, "ai1ec-calendar-title")]/text()').extract_first()
            year = 2018

        infos = response.xpath(
            '//div[contains(@class, "ai1ec-day")]').extract()

        for _, info in enumerate(infos):
            val = Selector(text=info)

            day = val.xpath(
                '//a[@class="ai1ec-load-view"]/text()').extract_first()

            titles = [x.strip().replace('@', '').replace('#', '') for x in val.xpath(
                '//span[@class="ai1ec-event-title"]/text()').extract() if x.strip() != '']
            locations = [x.strip().replace('@', '').replace('#', '') for x in val.xpath(
                '//span[@class="ai1ec-event-location"]/text()').extract() if x.strip() != '']

            if day and (len(titles) > 0):

                if day in days:
                    break
                else:
                    days.append(day)

                print('{}/{}/{}\n'.format(day, self.months.index(month)+1, year))
                for t, l in zip(titles, locations):
                    print('{}\t{}\n'.format(t, l))
