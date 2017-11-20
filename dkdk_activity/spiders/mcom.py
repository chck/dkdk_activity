# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.project import get_project_settings
from bs4 import BeautifulSoup
from dkdk_activity.items import DkdkActivityItem


class McomSpider(scrapy.Spider):
    name = 'mcom'
    allowed_domains = ['mixi.jp']
    start_urls = ['http://mixi.jp/']

    def __init__(self):
        self.settings = get_project_settings()

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'email': self.settings.get('MCOM_EMAIL'),
                'password': self.settings.get('MCOM_PW'),
            },
            callback=self.jump_to_target_after_login)

    def jump_to_target_after_login(self, response):
        return scrapy.Request(
            self.start_urls[0] + 'search_community.pl?search_type=event&search_mode=title&sort=event_start_date-a&category_id=0',
            callback=self.parse_events)

    def parse_events(self, response):
        for event in response.xpath('//div[@class="COMMUNITY_resultList__item"]').extract():
            event = BeautifulSoup(event, 'lxml')
            yield scrapy.Request(response.url,
                                 callback=self.parse_items,
                                 dont_filter=True,
                                 meta={'event': {
                                     'name': event.find('h3', class_='COMMUNITY_resultList__contentsTitle').a.text,
                                     'place': event.find('p', class_='COMMUNITY_resultList__eventDataContent COMMUNITY_resultList__eventDataContent--place').text,
                                     'member': event.find('li', class_='COMMUNITY_resultList__statusItem COMMUNITY_resultList__statusItem--member').text.replace('人が参加中', ''),
                                 }})

        next_page = response.xpath('//a[@class="COMMUNITY_pageNavigation__nextLink"]/@href').extract_first()
        if next_page:
            yield scrapy.Request(next_page,
                                 callback=self.parse_events)
        else:
            yield

    def parse_items(self, response):
        event = response.meta['event']
        return DkdkActivityItem(name=event['name'],
                                place=event['place'],
                                member=int(event['member']))
