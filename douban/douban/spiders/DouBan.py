# -*- coding: utf-8 -*-
import scrapy
from douban.items import DouBanItem


class DouBanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response):
        info = response.css("div.info")
        for i in info:
            item = DouBanItem()
            item['title'] = i.css("span.title::text").get()
            item['year'] = i.css("div.bd p::text")[1].get().split('/')[0].strip()
            item['country'] = i.css("div.bd p::text")[1].get().split('/')[1].strip()
            item['genre'] = i.css("div.bd p::text")[1].get().split('/')[2].strip()
            item['rating'] = i.css("span.rating_num::text").get()
            item['describe'] = i.css("span.inq::text").get()
            item['num'] = i.css("div.star span::text")[1].get()
            item['actor']  = i.css("div.bd p::text")[0].get().strip()
            yield item
        next_page = response.css("span.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)