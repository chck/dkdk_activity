# -*- coding: utf-8 -*-
import scrapy


class McomSpider(scrapy.Spider):
    name = 'mcom'
    allowed_domains = ['mcom.com']
    start_urls = ['http://mcom.com/']

    def parse(self, response):
        pass
