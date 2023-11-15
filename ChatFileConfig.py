import json


class Config():
    def __init__(self,config_file):
        self.config_file = config_file
        self.data_path = "./data" # 文件存储路径
        self.base_url = "https://api.openai.com/v1" # base_url
        self.api_key = "sk-..." # apiKey
        self.model = "gpt-3.5-turbo" # model
        self.length = 1024
        self.temperature = 0.7
        self.max_tokens = 1000
        self.sys_content = "你是一款文章阅读软件。接下来，用户将发送一个MD文件格式的文章。阅读后，你应该完全理解文章的内容，并能够以中文和Markdown格式对文章进行分析解读和回复与文章相关的问题。"
    
    # 导入配置数据
    def get_init(self):
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        self.data_path = config_data["data_path"]
        self.base_url = config_data['base_url']
        self.api_key = config_data["api_key"]
        self.model = config_data["model"]
        self.length = config_data["length"]
        self.temperature = config_data["temperature"]
        self.max_tokens = config_data["max_tokens"]
        self.sys_content = config_data["sys_content"]