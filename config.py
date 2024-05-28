import json
import os

class Config:
    def __init__(self, config_path=""):
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

        self.config_path = config_path

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
    

    @property
    def md_host(self):
        return self.config.get("md_host")
    
    @property
    def md_api_key(self):
        return self.config.get("md_api_key")


comfy_config = Config()


if __name__ == '__main__':
    print(Config().config_path)