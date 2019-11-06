# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import time

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class JdScrapySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class JdScrapyDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SeleniumMiddleware(object):

    def __init__(self):
        chrome_options = Options()
        # 设置headless模式
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # 设置不加载图片
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        self.browser = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=chrome_options)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        if spider.name == 'jd_phones':
            self.browser.get(request.url)
            
            if request.url == 'https://list.jd.com/list.html?cat=9987,653,655':
                self.browser.find_element_by_xpath(
                    '//div[@class="J_selectorLine s-brand"]//div[@class="sl-ext"]/a[text()="更多"]').click()
                time.sleep(1)
                
            # 只针对手机详情页，商品评论区的部分数据需要点击或者下拉才能异步加载
            if "item" in request.url:
                scroll_element = self.browser.find_element_by_xpath('//div[@id="comment"]')
                self.browser.execute_script('arguments[0].scrollIntoView();', scroll_element)
                WebDriverWait(self.browser, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[@class="comment-percent"]/div[@class="percent-con"]')))
                html = self.browser.page_source
                return HtmlResponse(url=self.browser.current_url, body=html, request=request, encoding='utf8')
            return HtmlResponse(url=self.browser.current_url, body=self.browser.page_source, request=request,
                                encoding='utf8')


class UserAgentMiddleware(object):
    def process_request(self, request, spider):
        request.headers[
            'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                            'Chrome/77.0.3865.90 Safari/537.36 '
