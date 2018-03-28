#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2018-03-27 17:43:48
# Project: brand

from pyspider.libs.base_handler import *
import os
import requests
import urllib
import re
import uuid
import json


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://www.sasa.com/brand', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            for each in response.doc('.brand-ware dd a').items():
                self.crawl(each.attr.href, callback=self.brand_page)
            
    @config(age=10 * 24 * 60 * 60)
    def brand_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            if re.match('http://www.sasa.com/gallery-index-n.*?$',each.attr.href):
                self.crawl(each.attr.href, callback=self.good_page)
    
    
    @config(age=10 * 24 * 60 * 60)
    def good_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            for each in response.doc('.arrivalslist li .arrivals-pic a').items():
                self.crawl(each.attr.href, callback=self.detail_page)
            for each in response.doc('.pageview .next').items():
                self.crawl(each.attr.href, callback=self.good_page)
    
    @config(priority=2)
    def detail_page(self, response):
        name = response.doc('.product-attributes .clearfix li:nth-child(2) .attributes-cont').text()
        brand_name = name.split('\xa0')[-1]
        
        good_zh_name = response.doc('.bread-crumbs h1').text()
        good_en_name = ''
        
        good_id = response.etree.xpath('//*[@id="product_container"]/form/input[3]')
        for good_id in good_id:
            good_id = good_id.get('value')
        
        product_id = response.etree.xpath('//*[@id="product_container"]/form/input[4]')
        for product_id in product_id:
            product_id = product_id.get('value')
        
        price_url = "http://www.sasa.com/product-ajax_product_store_and_price-{0}-{1}.html".format(good_id,product_id)
        html = requests.get(price_url).text
        text = json.loads(html)
        action_price = int(float(text['price']['price']))
        old_price = int(float(text['price']['mktprice']))
        
        dirpath = os.path.join(os.path.dirname(__file__),"images")
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            
        id = str(response.doc('.product-attributes ul.clearfix li:nth-child(1) div').text())

        image_url = response.etree.xpath('//div[@class="thumbnail"]/a')
        li = []
        for i in image_url:
            urls = i.get('href').split('?')[0]
            li.append(urls)
        
        for url in li:
            urllib.request.urlretrieve(url,"images/%s_%s.jpg" % (id,str(uuid.uuid4().hex)))
        
        a= [brand_name,good_zh_name,good_en_name,str(action_price),str(old_price),id]
        result = ",".join(a)
        with open('./coslib.txt','a') as f:
            f.write(result + '\n')
            
        return result
