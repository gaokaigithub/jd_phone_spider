# -*- coding: utf-8 -*-
from copy import deepcopy

# import pymysql
# import pymysql.cursors
# from twisted.enterprise import adbapi

from jd_scrapy.models import *


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class JdScrapyPipeline(object):

    def open_spider(self, spider):
        # 连接数据库，如果数据表不存在，则创建数据表
        db.connect()
        if not db.table_exists(['brand', 'good', 'goodreviewstag']):
            db.create_tables([Brand, Good, GoodReviewsTag])

    def close_spider(self, spider):
        db.close()

    def process_item(self, item, spider):
        # if isinstance(item, BrandItem):
        #     item.save()
        # elif isinstance(item, GoodItem):
        #     item.save()
        # elif isinstance(item,GoodReviewsTagItem):
        #     item.save()
        item.save()
        return item


# class MySQLPipeline(object):
#     '''同步写入mysql'''
#
#     def __init__(self):
#         self.conn = pymysql.connect('localhost', 'root', 'xinyuanchang', 'python_spider', 3306, charset='utf-8',
#                                     user_unicode=True)
#         self.cursor = self.conn.cursor()
#
#     def process_item(self, item, spider):
#         insert_sql = '''
#             insert into brand(id, name, phone_nums)
#             VALUES(%s, %s, %s)
#         '''
#         self.cursor.execute(insert_sql, (item['id'], item['name'], item['phone_nums']))
#         self.conn.commit()
#
#
# class MySQLTwistedPipeline(object):
#     """异步写入MySQL"""
#
#     def __init__(self, dbpool):
#         self.dbpool = dbpool
#
#     @classmethod
#     def from_settings(cls, settings):
#         dbparms = dict(
#             host=settings['MYSQL_HOST'],
#             db=settings['MYSQL_DBNAME'],
#             user=settings['MYSQL_USER'],
#             password=settings['MYSQL_PASSWORD'],
#             charset='utf-8',
#             cursorclass=cursors.DictCursor,
#             # user_unicode=True,
#         )
#
#         dbpool = adbapi.ConnectionPool('pymysql', **dbparms)
#         return cls(dbpool)
#
#     def process_item(self, item, spider):
#         # 使用twisted将mysql插入变成异步执行
#         query = self.dbpool.runInteraction(self.do_insert, item)
#         query.addErrback(self.handle_error, item, spider)  # or without item spider
#         return item
#
#     def handle_error(self, failure, item, spider):
#         # 处理异步插入的异常
#         print(failure)
#
#     def do_insert(self, item):
#         # 执行插入操作
#         # insert_sql = '''
#         #     insert into brand(id, name, phone_nums)
#         #     VALUES(%s, %s, %s)
#         # '''
#         # cursor.execute(insert_sql, (item['id'], item['name'], item['phone_nums']))
#         item.save()