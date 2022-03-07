
from selenium.webdriver.common.by import By
from src.tools import load_data, store_data
import traceback

from time import sleep
import json
import pandas as pd


class Crawler():
    filters = {}
    driver = None
    session_key = None
    session_password = None

    def __init__(self, website, s_key=None, s_password=None):
        self.load_parameters(website)
        self.session_key = s_key
        self.session_password = s_password    

    def load_parameters(self, website):
        with open('../data/crawler_settings.json') as f:
            loaded = json.load(f)

            website_settings = loaded["websites"][website]
            self.session_url = website_settings["session_url"]
            self.session_key_name = website_settings["session_key_name"]
            self.session_password_name = website_settings["session_password_name"]
            self.sumbmit_xpath = website_settings["sumbmit_xpath"]
            self.signin_form_xpath = website_settings["signin_form_xpath"]
            self.bot_trapped_class = website_settings["bot_trapped_class"]

            settings = loaded["settings"]["wait_time"]
            self.short_wait_time = settings["short_wait_time"]
            self.short_careful_wait_time = settings["short_careful_wait_time"]
            self.medium_wait_time = settings["medium_wait_time"]
            self.long_wait_time = settings["long_wait_time"]
            self.careful_wait_time = settings["careful_wait_time"]
            self.safe_wait_time = settings["safe_wait_time"]

            self.models = loaded["models"]

            if website in loaded["filters"]:
                self.filters = loaded["filters"][website]
            
    def initialize_driver(self, chromedriver):
        chromedriver.maximize_window()
        sleep(self.careful_wait_time)
        self.driver = chromedriver
        return chromedriver

    def login(self):
        self.access_url(self.session_url)

        if self.signin_form_xpath:
            self.driver.find_element(By.XPATH, self.signin_form_xpath).click()
            sleep(self.safe_wait_time)

        if self.sumbmit_xpath:
            username_input = self.driver.find_element(By.NAME, self.session_key_name)
            username_input.send_keys(self.session_key)
            sleep(self.medium_wait_time)

            password_input = self.driver.find_element(By.NAME, self.session_password_name)
            password_input.send_keys(self.session_password)
            sleep(self.medium_wait_time)

            self.driver.find_element(By.XPATH, self.sumbmit_xpath).click()
            sleep(self.safe_wait_time)
        else:
            print('Cannot login without Login Form data')

    def access_url(self, url):
        self.driver.get(url)
        sleep(self.long_wait_time)
    
    def access_component_by_xpath(self, x_path):
        return self.driver.find_elements(By.XPATH, x_path)
        
    def scroll_down_until_loaded(self):
        """A method for scrolling the page."""
        print('M: Scrolling down page until is fully loaded...')
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(self.long_wait_time)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def store_crawler_data(self, searched_data, model_name, query_used=None,
                           unique_subset=['link']):
        try:
            if searched_data and len(searched_data) > 0:
                data = pd.DataFrame(searched_data)

                data['dateParsed'] = pd.to_datetime('now')

                if query_used:
                    data['source'] = self.website
                    data['query'] = query_used

                # Load CSV if exists
                df = load_data(
                    self.models[model_name]['path'],
                    self.models[model_name]['columns']
                )  
                # Merge to CSV
                data = data.drop_duplicates(unique_subset, keep='first')
                df_merged = pd.concat([df[~df.link.isin(data.link)], data])
                df_merged = df_merged.drop_duplicates(unique_subset, keep='last')
                df_merged = df_merged.reset_index().drop('index', axis=1)

                # Store new CSV
                store_data(
                    df_merged,
                    self.models[model_name]['path'], 
                    self.models[model_name]['columns']
                )
        except Exception as e:
            print(traceback.format_exc())
            raise(e)
            