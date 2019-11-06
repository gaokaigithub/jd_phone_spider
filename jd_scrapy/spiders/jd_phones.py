# -*- coding: utf-8 -*-
import re
from abc import ABC
from urllib import parse

import scrapy
from scrapy.http import Request
from selenium.common.exceptions import NoSuchElementException

from jd_scrapy.items import *


# from jd_scrapy.jd_scrapy.items import BrandItem, GoodReviewsTagItem, GoodItem
# from jd_scrapy.jd_scrapy.items import BrandItem


class JdPhonesSpider(scrapy.Spider, ABC):
    name = 'jd_phones'
    allowed_domains = ['jd.com']
    # 京东商城"手机"列表页面
    start_urls = ['https://list.jd.com/list.html?cat=9987,653,655']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.domain = 'https://list.jd.com'

    def start_requests(self):
        yield Request(url=self.start_urls[0], callback=self.parse_brand)

    def parse_brand(self, response):
        brand_list = response.xpath('//ul[@id="brandsArea"]//li/a')
        for b in brand_list:
            brand_url = parse.urljoin(self.domain, b.xpath('./@href').extract()[0])
            b_id = b.xpath('../@id').extract()[0].strip()
            name = b.xpath('./@title').extract()[0].strip()
            # brand_url_linshi = 'https://list.jd.com/list.html?cat=9987,653,655&ev=exbrand_8557&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main'
            yield Request(url=brand_url, callback=self.parse_phone_list, meta={'b': b_id, 'n': name})

    def parse_phone_list(self, response):
        brand = BrandItem(b_id=response.meta['b'], name=response.meta['n'])
        
        brand['phone_nums'] = int(
            response.xpath('//div[@id="J_selector"]//div[@class="st-ext"]/span/text()').extract()[0])
        yield brand
        phone_hrefs = response.xpath(
            '//div[@id="plist"]//div[@class ="gl-i-wrap j-sku-item"]//div[contains(@class,"p-name")]/a/@href').extract()
        for href in phone_hrefs:
            url = parse.urljoin('https://', href)
            yield Request(url=url, callback=lambda response, it=response.meta['b']: self.parse_good(response, it),
                          dont_filter=True)
        next_page = response.xpath('//a[@class="pn-next"]/@href').extract()
        if next_page:
            next_page_href = next_page[0]
            next_page_url = parse.urljoin('https://list.jd.com', next_page_href)
            yield Request(url=next_page_url, callback=lambda response, it=response.meta['b']: self.parse_phone_list_2(response, it), dont_filter=True)

    def parse_phone_list_2(self, response, b_id):
        phone_hrefs = response.xpath(
            '//div[@id="plist"]//div[@class ="gl-i-wrap j-sku-item"]//div[contains(@class,"p-name")]/a/@href').extract()
        for href in phone_hrefs:
            url = parse.urljoin('https://', href)
            yield Request(url=url, callback=lambda response, it=b_id: self.parse_good(response, it), dont_filter=True)
        next_page = response.xpath('//a[@class="pn-next"]/@href').extract()
        if next_page:
            next_page_href = next_page[0]
            next_page_url = parse.urljoin('https://list.jd.com', next_page_href)
            yield Request(url=next_page_url, callback=lambda response, it=response.meta['b']: self.parse_phone_list_2(response, it), dont_filter=True)

    def process_value(self, num_str):
        '''
        将字符串类型的数字转换成数字
        :param num_str:字符串类型数字，可能包含"万"或"+"或"万+"
        :return:成功返回数字，默认返回0
        '''
        num = 0
        num = int(re.search(r'\D*(\d+\.?\d*).*', num_str).group(1))
        if "万" in num_str:
            num = num * 10000
        return num

    def parse_good(self, response, b_id):
        good = GoodItem()
        url = response.url
        good_id = int(re.search(r'.*/(\d+).html', url).group(1))

        name = "".join(response.xpath('//div[@class="sku-name"]/text()').extract()).strip()
        try:
            price = float(response.xpath('//span[@class="price J-p-{}"]/text()'.format(good_id)).extract()[0])
        except IndexError:
            price = 0.0
        # image_list = json.dumps(response.xpath('//div[@id="spec-list"]/ul').extract())
        try:
            colors = ','.join(response.xpath(
                '//div[@id="choose-attrs"]//div[@data-type="颜色"]//div[contains(@class,"item")]/@title').extract())
        except Exception as e:
            colors = ""
        try:
            memories = ','.join(response.xpath(
                '//div[@id="choose-attrs"]//div[@data-type="版本"]//div[contains(@class,"item")]/@title').extract())
        except Exception as e:
            memories = ""

        good['id'] = good_id
        good['name'] = name
        good['price'] = price
        good['brand'] = b_id
        good['colors'] = colors
        good['memories'] = memories

        # 获取商品评论区
        reviews_sel = response.xpath(
            '//div[@id="detail"]//li[contains(@clstag,"shangpin|keycount|product|shangpinpingjia")]')

        comment_percent_info = reviews_sel.xpath(
            '//div[@class="comment-percent"]/div[@class="percent-con"]/text()').extract()
        if comment_percent_info:
            comment_percent_str = comment_percent_info[0]
            comment_percent = int(re.search('(\d+)', comment_percent_str).group(1))
        else:
            comment_percent = 100

        com_filter_list = reviews_sel.xpath(
            '//div[@class="J-comments-list comments-list ETab"]/div[@class="tab-main small"]')

        image_comment_nums = 0
        video_comment_nums = 0
        added_comment_nums = 0
        positive_comment_nums = 0
        middle_comment_nums = 0
        negative_comment_nums = 0
        comment_nums_str = \
        com_filter_list.xpath('./ul/li[@clstag="shangpin|keycount|product|allpingjia"]/@data-num').extract()[0]
        comment_nums = self.process_value(comment_nums_str)
        if comment_nums > 0:
            image_comment_nums_str = \
            com_filter_list.xpath('./ul/li[@clstag="shangpin|keycount|product|shaidantab"]/@data-num').extract()[0]
            image_comment_nums = self.process_value(image_comment_nums_str)

            video_comment_nums_str = \
            com_filter_list.xpath('./ul/li[@clstag="shangpin|keycount|product|pingjiashipin"]/@data-num').extract()[0]
            video_comment_nums = self.process_value(video_comment_nums_str)

            added_comment_nums_str = \
            com_filter_list.xpath('./ul/li[@clstag="shangpin|keycount|product|zhuiping"]/@data-num').extract()[0]
            added_comment_nums = self.process_value(added_comment_nums_str)

            positive_comment_nums_str = \
            com_filter_list.xpath('./ul/li[@clstag="shangpin|keycount|product|haoping"]/@data-num').extract()[0]
            positive_comment_nums = self.process_value(positive_comment_nums_str)

            middle_comment_nums_str = \
            com_filter_list.xpath('./ul/li[@clstag="shangpin|keycount|product|zhongping"]/@data-num').extract()[0]
            middle_comment_nums = self.process_value(middle_comment_nums_str)

            negative_comment_nums_str = \
            com_filter_list.xpath('./ul/li[@clstag="shangpin|keycount|product|chaping"]/@data-num').extract()[0]
            negative_comment_nums = self.process_value(negative_comment_nums_str)

        good['comment_percent'] = comment_percent
        good['comment_nums'] = comment_nums
        good['image_comment_nums'] = image_comment_nums
        good['video_comment_nums'] = video_comment_nums
        good['added_comment_nums'] = added_comment_nums
        good['positive_comment_nums'] = positive_comment_nums
        good['middle_comment_nums'] = middle_comment_nums
        good['negative_comment_nums'] = negative_comment_nums

        yield good

        # 获取商品评价标签
        good_reviews_tag = GoodReviewsTagItem()
        good_reviews_tag['good'] = good_id
        tags_list = reviews_sel.xpath('//div[@clstag="shangpin|keycount|product|comment_icon"]/span')
        if tags_list:
            for tag_sel in tags_list:
                tag_id = tag_sel.xpath('./@data-id').extract()[0]
                tag_str = tag_sel.xpath('./text()').extract()[0]
                tag = re.search(r"(.+)\((\d+)\)", tag_str).group(1)
                tag_num = int(re.search(r"(.+)\((\d+)\)", tag_str).group(2))
                good_reviews_tag['id'] = tag_id
                good_reviews_tag['tag'] = tag
                good_reviews_tag['tag_num'] = tag_num

                yield good_reviews_tag
        else:
            tag_id = str(good_id)+"  no_tag"
            tag = ""
            tag_num = 0
            good_reviews_tag['id'] = tag_id
            good_reviews_tag['tag'] = tag
            good_reviews_tag['tag_num'] = tag_num

            yield good_reviews_tag
