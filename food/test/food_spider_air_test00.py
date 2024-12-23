# -*- coding: utf-8 -*-
"""
Created on 2024-11-26 14:32:09
---------
@summary:
---------
@author: auuo
"""
import pathlib
import time
import datetime
import json
import urllib
from urllib.parse import urlparse, urlunparse
import feapder
import re

from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CHROME_DRIVER = pathlib.Path('/Users/auuo/ff_test/feapder/food/spiders/chromedriver')
GECKODRIVER = '/Users/auuo/ff_test/food_feapder/food/geckodriver'

class FoodSpiderAir(feapder.AirSpider):
    # 中间件
    # def download_midware(self, request: Request):
    #     request.headers = {
    #     "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    #     }

    # def __init__(self, config_path, **kwargs):
    #     self.config_path = config_path
    #     super().__init__(**kwargs)

    def start_requests(self):
        # 读取json
        # json_url = input('JSON')

        # config
        # with open(self.config_path, 'r', encoding='utf-8') as f:
        #     data = json.load(f)

        with open('/Users/auuo/ff_test/food_feapder/food/data_2.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        item = dict(data)
        # 动态或静态
        dynamics_or_static = item['model']

        # 定义url地址
        url = item['url']
        # 使用urlparse解析URL
        parsed_url = urlparse(url)
        # 构造基础URL，只保留scheme（协议）、netloc（网络位置）和（可选的）params（参数，但通常不使用）
        base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
        item['base_url'] = base_url
        # print(base_url)

        # 解析a[href]
        item['tag_name'] = item['class'].split('[')[0]
        item['attr_name'] = item['class'].split('[')[1].split(']')[0]
        item['food_num'] = 0
        # 默认随机UA
        if dynamics_or_static == 1:
            # 静态
            yield feapder.Request(url, callback=self.static_parse, item=item)
        else:
            # 动态
            yield feapder.Request(url, callback=self.dynamics_parse, item=item)

    def static_parse(self, request, response):
        item = request.item
        attribute_key_contains = item['attributeKeyContains']
        # 提取网站链接
        a_list = []
        # 跳转a标签
        # html_response = response.open()
        # print(html_response)
        # all_response = response.Response.from_text(html=html_response, url=request.url)
        a_all = response.xpath(f"//{item['tag_name']}")  # class a[href]
        # 响应和源码不同
        # 写入配置文件
        # a_all = response.xpath("//li")

        for a in a_all:
            # 获取文章头 title
            a_title = a.xpath(f"./@{item['attributeKey']}").extract()

            # 响应和源码不同
            # a_title = a.xpath('./@data-title').extract()
            # print(a_title)

            a_content = a.xpath('./text()').extract()
            # print(a_content)
            # 转换成string
            a_title_string = ''.join(a_title)
            # print(a_title_string)
            a_content_string = ''.join(a_content)

            # 中文正则 href
            if (((re.findall(r"食品", a_title_string) != [])
                 and re.findall(attribute_key_contains, a_title_string) != [])
                 or(re.findall(r"食品", a_content_string) != []
                 and re.findall(attribute_key_contains, a_content_string) != [])):
                item['detail_url'] = a.xpath(f"./@{item['attr_name']}").extract()
                # item['detail_url'] = a.xpath('./@data-url').extract()

                detail_url = a.xpath(f"./@{item['attr_name']}").extract()
                # 响应和源码不同
                # detail_url = a.xpath('./@data-url').extract()
                detail_url_string = ''.join(detail_url)
                full = self.full_url(item['base_url'], detail_url_string)
                # 输出字页面
                print(full)
                yield feapder.Request(full, callback=self.detail_parse, item=item)
                time.sleep(0.5)

    def dynamics_parse(self, request, response):
        # json绑定
        item = request.item
        attribute_key_contains = item['attributeKeyContains']

        # 配置文件
        q1 = Options()
        q1.add_argument('--no-sandbox')
        q1.add_experimental_option('detach', True)
        # 导入driver
        service = Service(CHROME_DRIVER)
        # 创建浏览器对象
        # driver = webdriver.Chrome(service=service, options=q1)
        driver = webdriver.Firefox(GECKODRIVER)

        # 获取网址
        driver.get(response.url)
        time.sleep(3)

        iframes = driver.find_elements(By.TAG_NAME, "iframe")

        a_tags = driver.find_elements(By.TAG_NAME, 'a')
        # print(a_tags)
        # 遍历所有的 <a> 标签，获取 href 和 title
        for a in a_tags:
            a_title = a.get_dom_attribute('title')
            a_content = a.text
            # print(a_title)
            # print(a_content)
            if a_title is None:
                a_title = ''
            if a_content is None:
                a_content = ''
            a_title_string = ''.join(a_title) + 'a'
            a_content_string = ''.join(a_content) + 'a'

            if (((re.findall(r"食品", a_title_string) != [])
                 and re.findall(attribute_key_contains, a_title_string) != [])
                 or (re.findall(r"食品", a_content_string) != []
                 and re.findall(attribute_key_contains, a_content_string) != [])):
                a_url = a.get_dom_attribute('href')
                # full_url = self.full_url(item['base_url'], a_url)
                print(a_url)
                # if a_url == item['url']:
                #     break
                # yield feapder.Request(a_url, callback=self.detail_parse, item=item)

        driver.quit()

    def frame_parse(self, request, response):
        url = request.url
        # json绑定
        item = request.item
        attribute_key_contains = item['attributeKeyContains']
        item['base_url'] = url
        # 配置文件
        q1 = Options()
        q1.add_argument('--no-sandbox')
        q1.add_experimental_option('detach', True)
        # 导入driver
        service = Service(CHROME_DRIVER)
        # 创建浏览器对象
        driver = webdriver.Chrome(service=service, options=q1)

        item['base_url'] = url[:url.rfind('/') + 1]

        # 获取网址
        driver.get(response.url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        a_tags = soup.find_all('a')
        # print(a_tags)
        # 遍历所有的 <a> 标签，获取 href 和 title
        for a in a_tags:
            a_title = a.find('title')
            a_content = a.get_text()
            # print(a_title)
            # print(a_content)
            if a_title is None:
                a_title = ''
            if a_content is None:
                a_content = ''
            a_title_string = ''.join(a_title) + 'a'
            a_content_string = ''.join(a_content) + 'a'

            if (((re.findall(r"食", a_title_string) != [])
                 and re.findall(attribute_key_contains, a_title_string) != [])
                    or (re.findall(r"食", a_content_string) != []
                        and re.findall(attribute_key_contains, a_content_string) != [])):
                a_url = a.get('href')
                # print(a_url)
                full_url = self.full_url(item['base_url'], a_url)
                # print(full_url)

                yield feapder.Request(full_url, callback=self.detail_parse, item=item)
        driver.quit()


    def detail_parse(self, request, response):
        item = request.item
        try:
            download_all = response.xpath('//a')
            for download in download_all:
                # 网页文本判断
                download_content = download.xpath('./text()').extract()
                download_content_string = ''.join(download_content)
                download_list = download.xpath('./@href').extract()
                download_list_string = ''.join(download_list)
                # print(download_content_string)
                # TODO: xls, xlsx, doc, docx, pdf, zip
                if (re.findall(r"xls", download_list_string) != [] or
                    re.findall(r"xlsx", download_list_string) != [] or
                    re.findall(r"xls", download_content_string) != [] or
                    re.findall(r"xlsx", download_content_string) != [] or
                    re.findall(r"pdf", download_list_string) != [] or
                    re.findall(r"docx", download_list_string) != [] or
                    re.findall(r"zip", download_list_string) != []
                ):
                    # print(download_list_string)
                    item['food_num'] += 1
                    yield feapder.Request(download_list_string, callback=self.download_food, item=item)
                    time.sleep(0.5)
        except:
            print("error")

    def download_food(self, request, response):
        download_url = response.url
        print(download_url)

        file_name = download_url.split('/')[-1]
        # print(file_name)
        # 下载
        today_time = datetime.date.today()
        # if not pathlib.Path(f'./{today_time}').exists():
        #     pathlib.Path(f'./{today_time}').mkdir()
        #
        # with open(f'./{today_time}/{file_name}', 'wb') as f:
        #     f.write(response.content)
        print(request.item['food_num'])

    @staticmethod
    def full_url(base_url, href_url):

        if href_url.startswith("../../"):
            href_url = href_url.replace("../", "")
        if not href_url.startswith(("http://", "https://")):
            # 如果href是相对路径，进行拼接
            full_url = f"{base_url}/{href_url}"
        else:
            # 如果href是绝对路径，直接使用
            full_url = href_url
        return full_url


if __name__ == "__main__":
    FoodSpiderAir().start()
