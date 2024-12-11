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
from urllib.parse import urlparse, urlunparse
import feapder
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


CHROME_DRIVER = pathlib.Path('/Users/auuo/ff_test/feapder/food/spiders/chromedriver')
# 配置文件
q1 = Options()
q1.add_argument('--no-sandbox') # 沙盒模式
q1.add_experimental_option('detach', True)
# q1.add_argument("--headless")  # 启用无头模式


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
        num_json = input("数字")
        with open(f'/Users/auuo/ff_test/food_feapder/food/data_{num_json}.json',
                  'r', encoding='utf-8') as f:
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
        item['download_list_all'] = []
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
            if (((re.findall(r"食", a_title_string) != [])
                 and re.findall(attribute_key_contains, a_title_string) != [])
                 or(re.findall(r"食", a_content_string) != []
                 and re.findall(attribute_key_contains, a_content_string) != [])):
                item['detail_url'] = a.xpath(f"./@{item['attr_name']}").extract()
                # item['detail_url'] = a.xpath('./@data-url').extract()

                detail_url = a.xpath(f"./@{item['attr_name']}").extract()
                # 响应和源码不同
                # detail_url = a.xpath('./@data-url').extract()
                detail_url_string = ''.join(detail_url)
                full = self.full_url(item['base_url'], detail_url_string, item['url'])
                # 输出字页面
                print(full)
                yield feapder.Request(full, callback=self.detail_parse, item=item)
                time.sleep(0.5)

    def dynamics_parse(self, request, response):
        # json绑定
        item = request.item
        attribute_key_contains = item['attributeKeyContains']


        # 导入driver
        service = Service(CHROME_DRIVER)
        # 创建浏览器对象
        driver = webdriver.Chrome(service=service, options=q1)

        # 获取网址
        driver.get(response.url)

        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        temp = 1
        # TODO frame格式
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
                temp = 0
                a_url = a.get('href')
                # print(a_url)
                if a_url is None:
                    continue
                full_url = self.full_url(item['base_url'], a_url, item['url'])
                # print(full_url)
                # if a_url == item['url']:
                #     break
                item['download_list_all'].append(full_url)
                yield feapder.Request(full_url, callback=self.detail_parse, item=item)

        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes is not None and temp == 1:
            for iframe in iframes:
                iframe_src = iframe.get_dom_attribute('src')
                print('iframe_src:', iframe_src)
                yield feapder.Request(iframe_src, callback=self.frame_parse, item=item)
        driver.quit()


    def frame_parse(self, request, response):
        url = request.url
        # json绑定
        item = request.item
        attribute_key_contains = item['attributeKeyContains']
        item['base_url'] = url
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
                full_url = self.full_url(item['base_url'], a_url, item['url'])
                # print(full_url)
                item['download_list_all'].append(full_url)
                yield feapder.Request(full_url, callback=self.detail_parse, item=item)
        driver.quit()


    def detail_parse(self, request, response):
        item = request.item
        temp = 0
        try:
            time.sleep(1)
            download_all = response.xpath('//a')
            for download in download_all:
                # 网页文本判断
                download_content = download.xpath('./text()').extract()
                download_content_string = ''.join(download_content)
                download_list = download.xpath('./@href').extract()
                download_list_string = ''.join(download_list)
                # print(download_content_string)

                if (re.findall(r"xls", download_list_string) != [] or
                    re.findall(r"xlsx", download_list_string) != [] or
                    re.findall(r"xls", download_content_string) != [] or
                    re.findall(r"xlsx", download_content_string) != [] or
                    re.findall(r"pdf", download_list_string) != [] or
                    re.findall(r"docx", download_list_string) != [] or
                    re.findall(r"doc", download_list_string) != [] or
                    re.findall(r"zip", download_list_string) != []):
                    # print(download_list_string)
                    temp += 1
                    yield feapder.Request(download_list_string, callback=self.download_food, item=item)
                    time.sleep(0.5)
            # if temp == 0:
            #         yield feapder.Request(request.url, callback=self.detail_dynamic_parse, item=item)
        except:
            print("error")

    def detail_dynamic_parse(self, request, response):
        download_list_all = request.item['download_list_all']
        # 导入driver
        service = Service(CHROME_DRIVER)
        # 创建浏览器对象
        driver = webdriver.Chrome(service=service, options=q1)
        # print(download_list_all)
        for li in download_list_all[3:]:
            print(li)
            driver.get(li)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            a_tags = soup.find_all('a')
            for a in a_tags:
                # 网页文本判断
                a_href = a.get('href')
                a_content = a.get_text()
                # print(a_href)
                # print(a_content)
                if a_href is None:
                    a_href = ''
                if a_content is None:
                    a_content = ''
                a_href_string = ''.join(a_href)
                a_content_string = ''.join(a_content)
                if (re.findall(r"xls", a_href) != [] or
                        re.findall(r"xlsx", a_href_string) != [] or
                        re.findall(r"xls", a_content_string) != [] or
                        re.findall(r"xlsx", a_content_string) != [] or
                        re.findall(r"pdf", a_href_string) != [] or
                        re.findall(r"docx", a_href_string) != [] or
                        re.findall(r"zip", a_href_string) != []):
                    yield feapder.Request(a_href_string, callback=self.download_food, item=request.item)
                    driver.quit()

    def download_food(self, request, response):
        item = request.item
        download_url = response.url
        print(download_url)
        item['food_num'] += 1
        file_name = download_url.split('/')[-1]
        # print(file_name)
        # 下载
        today_time = datetime.date.today()
        # if not pathlib.Path(f'./{today_time}').exists():
        #     pathlib.Path(f'./{today_time}').mkdir()
        #
        # with open(f'./{today_time}/{file_name}', 'wb') as f:
        #     f.write(response.content)
        print(item['food_num'])


    @staticmethod
    def full_url(base_url, href_url, url):
        if href_url.startswith("./"):
            href_url = href_url.replace("./", "")
            full_url = f"{url}/{href_url}"
            return full_url
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
