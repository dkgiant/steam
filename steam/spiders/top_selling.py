# -*- coding: utf-8 -*-
import scrapy


class TopSellingSpider(scrapy.Spider):
    name = 'top_selling'
    allowed_domains = ['store.steampowered.com/search/?filter=topsellers']
    start_urls = ['http://store.steampowered.com/search/?filter=topsellers/']

    def parse(self, response):
        pass
