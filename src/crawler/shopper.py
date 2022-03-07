from src.tools import print_progress, latin_to_utf8
from src.crawler.master import Crawler
# from src.tools import strip_list
from parsel import Selector
import pandas as pd
import numpy as np

from selenium.webdriver.common.by import By
import re
from datetime import datetime
import unidecode

from time import sleep


class ShopperCrawler(Crawler):
    website = 'shopper'
    base_url = 'https://programada.shopper.com.br'
    sellers = {}

    def __init__(self, *args, **kwargs):
        super().__init__(self.website, *args, **kwargs)

        for seller in self.filters['sellers']:
            self.sellers[latin_to_utf8(seller['name'])] = seller['url']

    def parse_image_url(self, sel):
        image = None
        image_el = sel.xpath('//figure/@style').extract()
        if image_el and len(image_el) > 0:
            image = re.findall('url\(\"([\S]+)\"', image_el[0])
        if image and len(image) > 0:
            image = image[0]
        return image

    def parse_sellers(self, sel):
        sellers_xpath = "//div[contains(@class, 'sc-jibziO jUNAHb')]"

        sellers_prices = sel.xpath(sellers_xpath + '/span/text()').extract()
        sellers_prices = [latin_to_utf8(x) for x in sellers_prices[:int(len(sellers_prices)/2)]]

        sellers_names = sel.xpath(sellers_xpath + '/img/@src').extract()
        sellers_names = sellers_names[:int(len(sellers_names)/2)]
        sellers_names = [latin_to_utf8(key) for key, url in self.sellers.items() if url in sellers_names]

        parsed_sellers = dict(zip(sellers_names, sellers_prices))
        return parsed_sellers

    def parse_product_detail(self, sel, url):
        extraction_datetime = datetime.now()
        category = sel.xpath("//div[contains(@class, 'sc-epFoly RxyGD')]/text()").extract()
        price_to = sel.xpath("//div[contains(@class, 'sc-iKMXQg bhDFnM')]/span[2]/text()").extract()
        discount = sel.xpath("//div[contains(text(), 'economiza')]/span/text()").extract()
        name = sel.xpath("//h2[contains(@class, 'sc-bnOPBZ ljjuYX')]/text()").extract()

        response = {
            'name': name[0] if len(name) > 0 else None,
            'sku': None, 
            'department': 'Alimentos',
            'category': category[0] if len(category) > 0 else None,
            'url': url,
            'image': self.parse_image_url(sel),
            'price_to': price_to[0] if len(price_to) > 0 else None,
            'discount': discount[0] if len(discount) > 0 else None,
            'available': 'S',
            'stock_qty': None,
            'store': 'Shopper',
            'created_at': extraction_datetime.strftime('%Y-%m-%d'),
            'hour': extraction_datetime.strftime('%H:%M:%S'),
            'sellers': self.parse_sellers(sel)
        }

        return response

    def extract_products(self):
        sel = Selector(text=self.driver.page_source)

        subcategories_xpath = "//li[contains(@department, 'alimentos')]/div/ul/li/a/@href"
        product_details_button_xpath = "//button[contains(@class, 'sc-PZsNp fsKnKO')]"
        close_button_xpath = "//div/img[contains(@src, 'CloseIcon')]/.."
        subcategories_href = sel.xpath(subcategories_xpath).extract()
        subcategories_href = subcategories_href[1:]
        print_progress_title = 'Products'

        parsed_products = []

        for href in subcategories_href:
            self.access_url(self.base_url + href)
            self.scroll_down_until_loaded()

            p_detail_buttons = self.access_component_by_xpath(product_details_button_xpath)
            for button in p_detail_buttons:
                sel = Selector(text=self.driver.page_source)
                print_progress(subcategories_href.index(href),
                               len(subcategories_href), title=print_progress_title,
                               current_file=f'{p_detail_buttons.index(button)+1}/{len(p_detail_buttons)}')
                self.driver.execute_script("arguments[0].click();", button)

                sleep(self.short_careful_wait_time)
                sel = Selector(text=self.driver.page_source)
                parsed_product = self.parse_product_detail(sel, self.base_url + href)
                parsed_products.append(parsed_product)
                
                for _ in range(10):
                    try:
                        close_button = self.access_component_by_xpath(close_button_xpath)
                        self.driver.execute_script("arguments[0].click();", close_button[0])
                        break
                    except IndexError as e:
                        sleep(self.short_wait_time)
                       
        print_progress(1, 1, title=print_progress_title)
        return parsed_products