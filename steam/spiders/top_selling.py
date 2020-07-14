# -*- coding: utf-8 -*-
import scrapy
from w3lib.html import remove_tags
from ..items import SteamItem
import json
from scrapy.selector import Selector


class TopSellingSpider(scrapy.Spider):
    name = 'top_selling'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['https://store.steampowered.com/search/?filter=topsellers']
    start_postion = 0
    total_count = 200
    count = 50    

    def parse(self, response):
        html_obj = response.text
        self.parse_selector(html_obj)
        print('run here 1?')
        # TODO:
        # - function parse_slector not run 
    def before_parse(self, response):
        result = json.loads(response.body)
        self.total_count = result.get('total_count')
        html_obj = result.get('results_html')
        html_obj = html_obj.replace("\r\n", '')
        html_obj = html_obj.replace("\t\t", '')
        self.parse_selector(html_obj)

    def parse_selector(self, html_obj):
        print('run here 2?')
        steam_item = SteamItem()
        resp = Selector(text=html_obj)
        list_game = resp.xpath(r'//div[@id="search_resultsRows"]/a')

        for game in list_game:
            steam_item['game_url'] = game.xpath(r'.//@href').get()
            steam_item['img_url'] = game.xpath(
                r'.//div[@class="col search_capsule"]/img/@src').get()
            steam_item['game_name'] = game.xpath(
                r'.//span[@class="title"]/text()').get()
            steam_item['release_date'] = game.xpath(
                r'.//div[@class="col search_released responsive_secondrow"]/text()').get()
            steam_item['platforms'] = self.get_platforms(game.xpath(
                r'.//span[contains(@class,"platform_img") or @class="vr_supported"]/@class').getall())
            steam_item['reviews_summary'] = self.remove_html(game.xpath(
                r'.//span[contains(@class,"search_review_summary")]/@data-tooltip-html').get())
            steam_item['discount_rate'] = self.clean_discount_rate(game.xpath(
                r'.//div[contains(@class,"search_discount")]/span/text()').get())
            steam_item['original_price'] = self.get_original_price(game.xpath(
                r'.//div[contains(@class,"search_price_discount_combined")]'))
            steam_item['discounted_price'] = game.xpath(
                r'normalize-space(.//div[contains(@class,"search_price discounted")]/text()[2])').get()

            yield steam_item
        self.start_postion += self.count
        if self.start_postion < self.total_count:
            yield scrapy.Request(
                url=f'https://store.steampowered.com/search/results/?query&start={self.start_postion}&count={self.count}&dynamic_data=&sort_by=_ASC&snr=1_7_7_topsellers_7&filter=topsellers&infinite=1',
                callback=self.before_parse
            )



    def get_platforms(self, list_classes):
        platforms = []
        for item in list_classes:
            platform = item.split(' ')[-1]
            if platform == 'win':
                platforms.append('Windows')
            if platform == 'mac':
                platforms.append('Mac os')
            if platform == 'linux':
                platforms.append('Linux')
            if platform == 'vr_supported':
                platforms.append('VR Supported')

        return platforms

    def remove_html(self, reviews_summary):
        cleaned_review_summary = ''

        try:
            cleaned_review_summary = remove_tags(reviews_summary)
        except TypeError:
            cleaned_review_summary = 'no reviews'

        return cleaned_review_summary

    def clean_discount_rate(self, discount_rate):
        if discount_rate:
            return discount_rate.lstrip('-')
        return discount_rate

    def get_original_price(self, selector_obj):
        original_price = ''
        div_with_discount = selector_obj.xpath(
            r'.//div[contains(@class,"search_price discounted")]')
        if len(div_with_discount) > 0:
            original_price = div_with_discount.xpath(
                r'.//span/strike/text()').get()
        else:
            original_price = selector_obj.xpath(
                r'normalize-space(.//div[contains(@class,"search_price")]/text())').get()

        return original_price
