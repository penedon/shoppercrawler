import json

class CrawlerConfig:
    default_crawler_settings_path = '../data/crawler_settings.json'

    def __init__(self):
        self.load_settings()

    def load_settings(self):
        with open(self.default_crawler_settings_path) as f:
            loaded = json.load(f)
            settings = loaded["settings"]["wait_time"]
            self.short_wait_time = settings["short_wait_time"]
            self.medium_wait_time = settings["medium_wait_time"]
            self.careful_wait_time = settings["careful_wait_time"]
            self.safe_wait_time = settings["safe_wait_time"]
            
            self.models = loaded["models"]
