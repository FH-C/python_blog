# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DouBanItem(scrapy.Item):
    title = scrapy.Field()
    year = scrapy.Field()
    country = scrapy.Field()
    genre = scrapy.Field()
    rating = scrapy.Field()
    describe = scrapy.Field()
    num = scrapy.Field()
    actor = scrapy.Field()