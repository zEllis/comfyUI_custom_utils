
import requests
import json
import asyncio
import aiohttp
import time
from .config import comfy_config


REFRESH_TIME = 5
TIMEOUT = 60*5*10
EXCEPTION_TIMEOUT = 60*10

class Mdjourney:
    async def post(self, path, data):
        if isinstance(data, dict):
            data = json.dumps(data)
        url = comfy_config.md_host + path

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers={"Content-Type": "application/json", "mj-api-secret": comfy_config.md_api_key}) as response:
                json_res = await response.json()
                print(f"md post, path:{path}, data:{data}, resp:{json_res}")
                return json_res


    async def get(self, path):
        url = comfy_config.md_host + path
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers={"Content-Type": "application/x-www-form-urlencoded",  "mj-api-secret": comfy_config.md_api_key}) as response:
                json_res = await response.json()
                print(f"md get, path:{path}, resp:{json_res}")
                return json_res



    async def imagine(self, prompt):
        path = "/mj/submit/imagine"

        data = {
            "botType": "MID_JOURNEY",
            "prompt": prompt,
        }
        resp = await self.post(path, data)
        task_id = resp.get("result")
        task_result = {}
        task_status = "init"
        start_time  = time.time()
        while task_status in ["init","SUBMITTED", "IN_PROGRESS", "NOT_START"]:
            print(f"waiting for imagine, task_status: {task_status}, time_cost:{int(time.time() - start_time)}s")
            if task_status in ["SUBMITTED", "NOT_START"] and time.time() - start_time > EXCEPTION_TIMEOUT:
                raise Exception(f"task_status is {task_status} over 60s, please retry")
            await asyncio.sleep(REFRESH_TIME)
            task_result = await self.query_sinlge_result(id=task_id)
            task_status = task_result.get("status")
            
            if time.time() - start_time > TIMEOUT:
                return {"error": "timeout"}
            if task_status == "SUCCESS":
                return task_result   # imageUrl
        else:
            return {
                "error": f"task status invalid , {task_status}"
            }

    async def query_sinlge_result(self, id):

        path = "/mj/task/list-by-condition"

        data = {
            "ids": [id]
        }
        resp = await self.post(path, data)

        return resp[0]


    async def action(self, custom_id, task_id):
        path = "/mj/submit/action"
        data = {
            "customId": custom_id, # "MJ::JOB::upsample::2::2e694edd-7273-4c8f-9a07-a22e7f9c84f0",
            "taskId": task_id, # "1715050079653376"
        }
        resp = await self.post(path, data)

        task_id = resp.get("result")
        task_result = {}
        task_status = "init"
        start_time = time.time()
        while task_status in ["init","SUBMITTED", "IN_PROGRESS", "NOT_START"]:
            print(f"waiting for imagine, task_status: {task_status}, time_cost:{int(time.time() - start_time)}s")
            if task_status in ["SUBMITTED", "NOT_START"] and time.time() - start_time > EXCEPTION_TIMEOUT:
                raise Exception(f"task_status is {task_status} over 60s, please retry")
            await asyncio.sleep(REFRESH_TIME)
            task_result = await self.query_sinlge_result(id=task_id)
            task_status = task_result.get("status")
            if time.time() - start_time > TIMEOUT:
                return {"error": "timeout"}
            if task_status == "SUCCESS":
                return task_result  # imageUrl
        else:
            return {
                "error": f"task status invalid , {task_status}"
            }
    

    async def _get_image_batch_index(self, prompt, image_index_list=None, thumbnail=False):
        # 输入提示词， 返回图像列表
        # thumbnail: 是否返回缩略图
        # image_index_list: 要选择的图像索引， 索引从1开始
        # return: [iamge_url, ]
        if not image_index_list:
            image_index_list = [1]
        # imagine_result = await self.imagine(prompt)
        # task_id = imagine_result.get("result")
        
        imagine_result = await self.imagine(prompt)
        print(f"imagine_result:{imagine_result}")
        if "error" in imagine_result:
            
            raise Exception("Error: {}".format(imagine_result.get("error")))
        thumb_image_url = imagine_result.get("imageUrl")  # 缩略图
        if thumbnail:
            
            return [thumb_image_url]
        button_dict = {}
        buttons = imagine_result["buttons"]
        task_id = imagine_result.get("id")
        for item in buttons:
            custom_id = item["customId"]
            label = item["label"]
            button_dict[label] = custom_id

        target_upscale_image_id = [button_dict[f"U{i}"] for i in image_index_list]

        target_upscale_image_tasks = [
            self.action(id, task_id) for id in target_upscale_image_id
        ]
        
        results = await asyncio.gather(*target_upscale_image_tasks)
        print(f"after action, results:{results}")
        results = [item["imageUrl"] for item in results]
        results.insert(0, thumb_image_url)
        return results


    async def _get_image_batch(self, prompt_list, image_index, thumbnail=False):
        # 输入提示词， 返回图像列表
        # thumbnail: 是否返回缩略图
        # image_index_list: 要选择的图像索引， 索引从1开始
        # return: [iamge_url, ]
        if not image_index:
            image_index = 1
        # imagine_result = await self.imagine(prompt)
        # task_id = imagine_result.get("result")
        imagine_tasks = [
            self.imagine(p) for p in prompt_list
        ]
        imagine_results = await asyncio.gather(*imagine_tasks)

        print(f"imagine_result:{imagine_results}")
        # if "error" in imagine_result:
        #     raise Exception("Error: {}".format(imagine_result.get("error")))
        thumb_image_url_list = [imagine_result.get("imageUrl") for imagine_result in imagine_results]  # 缩略图
        if thumbnail:
            return thumb_image_url_list

        target_upscale_image_tasks = []

        for imagine_result in imagine_results:
            buttons = imagine_result["buttons"]
            task_id = imagine_result.get("id")
            for item in buttons:
                custom_id = item["customId"]
                label = item["label"]
                if label == f"U{image_index}":
                    target_upscale_image_tasks.append(self.action(custom_id, task_id))
                    break

        results = await asyncio.gather(*target_upscale_image_tasks)
        print(f"after action, results:{results}")
        results = [item["imageUrl"] for item in results]
        results.insert(0, thumb_image_url_list)
        return results




    def get_image(self, prompt, image_index=None, thumbnail=False, type="single"):

        if type == "single":
            return asyncio.run(self._get_image_batch_index(prompt, image_index_list=[image_index], thumbnail=thumbnail))
        elif type == "batch":
            return asyncio.run(self._get_image_batch(prompt_list=prompt, image_index=image_index, thumbnail=thumbnail))
        else:
            raise ValueError(f"Unknown type {type}")


midjouney_async = Mdjourney()

            
        
        
        