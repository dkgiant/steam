# -*- coding: utf-8 -*-
import scrapy

from ..items import SteamItem
import json
from scrapy.selector import Selector
from scrapy.loader import ItemLoader


class TopSellingSpider(scrapy.Spider):
    name = 'top_selling'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['https://store.steampowered.com/search/?filter=topsellers']
    start_postion = 0
    total_count = 200
    count = 50
    html = ''

    def parse(self, response):
        self.html = response.text
        yield scrapy.Request(
            url=response.url,
            callback=self.parse_selector
        )

        # TODO:
        # - function parse_slector not run
    def before_parse(self, response):
        result = json.loads(response.text)
        self.total_count = result.get('total_count')
        self.html = result.get('results_html')
        self.html = self.html.replace("\r\n", '')
        self.html = self.html.replace("\t\t", '')

        yield scrapy.Request(
            url=response.url,
            callback=self.parse_selector,
            dont_filter=True
        )

    def parse_selector(self, response):        
        resp = Selector(text=self.html)
        list_game = resp.xpath(r'//div[@id="search_resultsRows"]/a')
        if len(list_game) == 0:
            list_game = resp.xpath(r'//a')

        for game in list_game:
            loader = ItemLoader(item=SteamItem(), selector=game, response=resp)
            loader.add_xpath('game_url', r'.//@href')
            loader.add_xpath(
                'img_url', r'.//div[@class="col search_capsule"]/img/@src')
            loader.add_xpath('game_name', r'.//span[@class="title"]/text()')
            loader.add_xpath(
                'release_date', r'.//div[@class="col search_released responsive_secondrow"]/text()')
            loader.add_xpath(
                'platforms', r'.//span[contains(@class,"platform_img") or @class="vr_supported"]/@class')
            loader.add_xpath(
                'reviews_summary', r'.//span[contains(@class,"search_review_summary")]/@data-tooltip-html')
            loader.add_xpath(
                'discount_rate', r'.//div[contains(@class,"search_discount")]/span/text()')
            loader.add_xpath(
                'original_price', r'.//div[contains(@class,"search_price_discount_combined")]')
            loader.add_xpath(
                'discounted_price', r'normalize-space(.//div[contains(@class,"search_price discounted")]/text()[2])')
            yield loader.load_item()
        self.start_postion += self.count
        if self.start_postion < self.total_count:
            yield scrapy.Request(
                url=f'https://store.steampowered.com/search/results/?query&start={self.start_postion}&count={self.count}&dynamic_data=&sort_by=_ASC&snr=1_7_7_topsellers_7&filter=topsellers&infinite=1',
                callback=self.before_parse
            )


    




   
