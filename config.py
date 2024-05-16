import json
import os

class Config:
    def __init__(self, config_path=""):
        if not config_path:
            config_path = os.path.abspath(os.path.dirname(__file__), "config.json")
        
        self.check_config(config_path)
        
    def check_config(self, config_path):
        if not os.path.exists(config_path):
            raise ValueError("Config file '%s' does not exist" % config_path)
        if not config_path.endswith(".json"):
            raise ValueError("Config file '%s' does not end with .json" % config_path)

        self.config = json.load(open(config_path, "r"))

    @property
    def gpt_api_key(self):
        return self.config.get("chatgpt_api_key")
