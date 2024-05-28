
import requests
import json
import asyncio

from .config import comfy_config

class Mdjourney:
    def post(self, path, data):
        if isinstance(data, dict):
            data = json.dumps(data)
        url = comfy_config.md_host + path

        r = requests.post(url, data,headers={"Content-Type": "application/json", "mj-api-secret": comfy_config.md_api_key})

        print("post", path, r.status_code)
        print(r.content)
        return r.json()


    def get(self, path):
        url = comfy_config.md_host + path
        r = requests.get(url, headers={"Content-Type": "application/x-www-form-urlencoded",  "mj-api-secret": comfy_config.md_api_key})

        print("get", path, r.status_code)
        print(r.content)
        return r.json()


    def imagine(self, prompt):
        path = "/mj/submit/imagine"

        data = {
            "botType": "MID_JOURNEY",
            "prompt": prompt,
        }

        return self.post(path, data)


    def query_result(self, id):

        path = "/mj/task/list-by-condition"

        data = {
            "ids": [id]
        }

        return self.post(path, data)


    def action(self, custom_id, task_id):
        path = "/mj/submit/action"
        data = {
            "customId": custom_id, # "MJ::JOB::upsample::2::2e694edd-7273-4c8f-9a07-a22e7f9c84f0",
            "taskId": task_id, # "1715050079653376"
        }
        return self.post(path, data)


    def get_image(self, prompt, image_index_list=None, thumbnail=False):
        # 输入提示词， 返回图像列表
        # thumbnail: 是否返回缩略图
        if not image_index_list:
            image_index_list = [0]
        imagine_result = self.imagine(prompt)
        task_id = imagine_result.get("result")

        task_result = self.query_result(id=task_id)
        task_status = task_result.get("status")
        