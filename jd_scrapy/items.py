# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from jd_scrapy.models import *


# class JdScrapyItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass


class BrandItem(scrapy.Item):
    b_id = scrapy.Field()
    name = scrapy.Field()
    phone_nums = scrapy.Field()

    def save(self):
        brand = Brand()
        brand.id = self['b_id']
        brand.name = self['name']
        brand.phone_nums = self['phone_nums']

        existed_brand = Brand.select().where(Brand.id == brand.id)
        if existed_brand:
            brand.save()
        else:
            brand.save(force_insert=True)


class GoodItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    colors = scrapy.Field()
    memories = scrapy.Field()
    comment_percent = scrapy.Field()
    comment_nums = scrapy.Field()
    image_comment_nums = scrapy.Field()
    video_comment_nums = scrapy.Field()
    added_comment_nums = scrapy.Field()
    positive_comment_nums = scrapy.Field()
    middle_comment_nums = scrapy.Field()
    negative_comment_nums = scrapy.Field()

    def save(self):
        good = Good(brand=self['brand'])
        good.id = self['id']
        good.name = self['name']
        # good.brand_id = self['brand'][0]
        good.price = self['price']
        good.colors = self['colors']
        good.memories = self['memories']
        good.comment_percent = self['comment_percent']
        good.comment_nums = self['comment_nums']
        good.image_comment_nums = self['image_comment_nums']
        good.video_comment_nums = self['video_comment_nums']
        good.added_comment_nums = self['added_comment_nums']
        good.positive_comment_nums = self['positive_comment_nums']
        good.middle_comment_nums = self['middle_comment_nums']
        good.negative_comment_nums = self['negative_comment_nums']

        existed_good = Good.select().where(Good.id == good.id)
        if existed_good:
            good.save()
        else:
            good.save(force_insert=True)


class GoodReviewsTagItem(scrapy.Item):
    id = scrapy.Field()
    good = scrapy.Field()
    tag = scrapy.Field()
    tag_num = scrapy.Field()

    def save(self):
        good_reviews_tag = GoodReviewsTag(good=self['good'])
        good_reviews_tag.id = self['id']
        # good_reviews_tag.good_id = self['good']
        good_reviews_tag.tag = self['tag']
        good_reviews_tag.tag_num = self['tag_num']

        exist_tag = GoodReviewsTag.select().where((GoodReviewsTag.good_id == good_reviews_tag.good_id) & (GoodReviewsTag.tag == good_reviews_tag.tag))
        if exist_tag:
            good_reviews_tag.save()
        else:
            i = 0
            while GoodReviewsTag.select().where(GoodReviewsTag.id == good_reviews_tag.id):
                i = i+1
                good_reviews_tag.id = good_reviews_tag.id + " " + str(i)
            good_reviews_tag.save(force_insert=True)
