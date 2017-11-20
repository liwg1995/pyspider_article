#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-11-20 11:26:41
# Project: v2ex

from pyspider.libs.base_handler import *
import re 
import random
import pymysql

class Handler(BaseHandler):
    crawl_config = {
    }
    
    # def __int__(self):
        
    def add_question(self,title,content):
        db = pymysql.connect('localhost','root','root','wen')
        try:
            cursor = db.cursor()
            sql = 'insert into question(title, content, user_id, create_date) values ("%s","%s",%d,%s)' % (title, content, random.randint(1,10), 'now()');

            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.v2ex.com/', callback=self.index_page, validate_cert=False)
        
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="https://www.v2ex.com/?tab="]').items():
            self.crawl(each.attr.href, callback=self.tab_page, validate_cert=False)
            
    @config(age=10 * 24 * 60 * 60)
    def tab_page(self, response):
        for each in response.doc('a[href^="https://www.v2ex.com/go/"]').items():
            self.crawl(each.attr.href, callback=self.board_page, validate_cert=False)
            
    @config(age=10 * 24 * 60 * 60)
    def board_page(self, response):
        for each in response.doc('a[href^="https://www.v2ex.com/t/"]').items():
            url = each.attr.href
            if url.find('#reply')>0:
                url = url[0:url.find('#')]
            self.crawl(url, callback=self.detail_page, validate_cert=False)
        for each in response.doc('a.page_normal').items():
            self.crawl(each.attr.href, callback=self.board_page, validate_cert=False)
            
    @config(priority=2)
    def detail_page(self, response):
        title = response.doc('h1').text()
        content = response.doc('div.topic_content').html().replace('"', '\\"')
        self.add_question(title, content)  #插入数据库
        return {
            "url": response.url,
            "title": title,
            "content": content,
        }

