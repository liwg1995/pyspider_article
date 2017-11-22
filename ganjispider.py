#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-20 18:20:01
# Project: ganjiwang

from pyspider.libs.base_handler import *
import re
import json
class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://www.ganji.com/index.htm', callback=self.city_page,validate_cert=False)

    @config(age=10 * 24 * 60 * 60)
    def city_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            if re.match("http://[\s\S]*.ganji.com/",each.attr.href):
                #if re.match("http://[^tuiguang]*.ganji.com/",each.attr.href):
                    #if re.match("http://[^mobile]*.ganji.com/",each.attr.href):
                        self.crawl(each.attr.href + 'fang1/', callback=self.fang_page,validate_cert=False)
                        
    @config(age=10 * 24 * 60 * 60)                 
    def fang_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            if re.match("http://[\s\S]*.ganji.com/fang1/\d.*$",each.attr.href):
                self.crawl(each.attr.href, callback=self.detail_page,validate_cert=False)
        for each in response.doc('a[href^="http"]').items():
            if re.match("http://[\s\S]*.ganji.com/fang1/^o\d{1,}/",each.attr.href):
                self.crawl(each.attr.href, callback=self.fang_page,validate_cert=False)
        
    @config(priority=2)
    def detail_page(self, response):
        phone = response.doc('div.c_phone').attr('data-phone')
        name = response.doc('p.name').text()
        if "个人" in name:
            name = name.split("(")[0]
            type = "房东"
        else:
            type = "房屋租赁中介"
        address = response.doc('a.fc-city').text()  
        #weizhi = response.etree.xpath("*[@class='info f-clear']/li[2]/text()")
        webside = "赶集网"
        a = {
            "url": response.url,
            "title": response.doc('title').text(),
            "phone": phone,
            "name": name,
            "type": type,
            "address": address,
            #"weizhi": weizhi,
            "website": webside,
           
        }
	b = a.values()
        c = sorted(b)
        result = ",".join(c)
        with open("result.txt","a") as f:
            f.write(result + '\n')
        return result

