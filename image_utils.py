import aiohttp
import asyncio
import json
import torch
import numpy as np
import comfy.utils
from comfy.cli_args import args
from folder_paths import output_directory, get_save_image_path

from .utils import tensor_to_pil, pil_to_tensor, get_text_size
from .base_node import Base, ANY
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageChops
from PIL.PngImagePlugin import PngInfo

from . import utils
from .chatgpt import open_ai_client, open_ai_client_async
from .md_async import midjouney_async
import sys
import os
import logging
import time


my_dir = os.path.dirname(os.path.abspath(__file__))
custom_nodes_dir = os.path.abspath(os.path.join(my_dir, ".."))
comfy_dir = os.path.abspath(os.path.join(my_dir, "..", ".."))

# Construct the path to the font file
font_path = os.path.join(my_dir, "arial.ttf")

# Append comfy_dir to sys.path & import files
sys.path.append(comfy_dir)

from nodes import PreviewImage


class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


ANY = AnyType("*")


class Base:

    CATEGORY = "bf"
    FUNCTION = "func"
    RETURN_TYPES = ()


class GetTitleByIndex(Base):
    RETURN_TYPES = ("STRING", "INT")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "all_prompt": ("STRING", {"default": "default_title"}),
                "index": ("INT", {"default": 1, "min": 1, "max": 50, "step": 1}),
            },
        }

    def func(self, all_prompt, index):
        print(all_prompt)
        print(type(all_prompt))

        all_prompt_dict = "{" + all_prompt + "}"
        all_prompt_dict = json.loads(all_prompt_dict)
        title = all_prompt_dict.get(str(index - 1)) or "default title"
        return title, index


class AddTitleToImage(Base):
    # 为生成的图片添加title

    RETURN_TYPES = ("IMAGE", "STRING")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "print_to_screen": (["enable", "disable"],),
                "title": ("STRING", {"default": "default_title"}),
                "font_size": (
                    "INT",
                    {
                        "default": -1,
                        "min": -2,
                        "max": 1000,
                        "step": 2,
                        "display": "-1表示自适应",
                    },
                ),
                "font_path": (
                    "STRING",
                    {
                        "default": "C:\\Users\\Admin\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Neuron Regular.otf"
                    },
                ),
                "text_color": ("STRING", {"default": "#FFFFFF"}),
            },
        }

    def add_title(self, pil_image, title, text_color=None, font_path=None, font_size=0):
        font_path = (
            font_path
            or "C:\\Users\\Admin\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Neuron Regular.otf"
        )
        image_width, image_height = pil_image.size
        if font_size <= 0:
            font_size = image_width // 10
        font = ImageFont.truetype(font_path, font_size)
        text_image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))

        text_draw = ImageDraw.Draw(text_image)
        # 获取文本大小
        text_bbox = text_draw.textbbox((0, 0), title, font=font)

        # 计算文本宽度和高度
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # 计算文本位置
        x = (image_width - text_width) / 2
        y = image_height - text_height - image_height // 10

        text_color = text_color or (255, 255, 255)  # 完全不透明的白色
        text_draw.text((x, y), title, font=font, fill=text_color)
        # 将文本图片合并到原始图片上
        combined = Image.alpha_composite(pil_image.convert("RGBA"), text_image)

        return combined

    def func(
        self,
        image,
        title,
        print_to_screen="enable",
        font_path=None,
        font_size=0,
        text_color=None,
    ):
        if print_to_screen == "enable":
            print(
                f"""Your input contains:
                string_field aka input text: {title}
            """
            )
        new_str = f"add_title_{title}"
        image1 = image[0]
        pil_image = tensor_to_pil(image1)
        pil_image = self.add_title(pil_image, title, text_color, font_path, font_size)
        pil_image.save(
            "E:\\AI\\ComfyUI_windows_portable_nvidia_cu121_or_cpu\\ComfyUI_windows_portable\\output\\from_tensor_{}.png".format(
                int(time.time())
            )
        )

        tensor_image = pil_to_tensor(pil_image)
        return (tensor_image, new_str)


class AddTitleToAlbum(Base):
    # RETURN_TYPES = ("IMAGE",)
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE")
    card_width, card_height = 210, 260
    default_font_path = "C:\\Users\\Admin\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Neuron Regular.otf"

    default_album_width, default_album_height = 2339, 1080

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "all_prompt": ("STRING", {"default": "default_title"}),
                "font_size": (
                    "INT",
                    {
                        "default": -1,
                        "min": -2,
                        "max": 1000,
                        "step": 2,
                        "display": "-1表示自适应",
                    },
                ),
                "font_path": (
                    "STRING",
                    {
                        "default": "C:\\Users\\Admin\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Neuron Regular.otf"
                    },
                ),
                "text_color": ("STRING", {"default": "#FFFFFF"}),
            },
        }

    @property
    def card_pos_config(self):
        return {
            1: (590, 530),
            2: (877, 518),
            3: (1167, 518),
            4: (1452, 520),
            5: (1738, 530),
            6: (590, 877),
            7: (878, 862),
            8: (1164, 857),
            9: (1455, 867),
            10: (1738, 875),
        }

    def get_text_pos_by_config(self, draw, font, index, text):

        w, h = self.card_pos_config.get(index) or (0, 0)
        text_width, text_height = get_text_size(draw, font, text)

        text_start_width = w - text_width // 2
        text_start_height = h - text_height // 2

        return text_start_width, text_start_height

    def parse_all_prompt_to_dict(self, all_prompt):
        all_prompt_dict = "{" + all_prompt + "}"
        all_prompt_dict = json.loads(all_prompt_dict)
        return all_prompt_dict

    def auto_font_size(self, longest_text):
        font_size = (self.card_width // len(longest_text)) or 1
        print(
            f"auto font_size, card_width: {self.card_width}, longest_text: {longest_text}, length:{len(longest_text)}, font_size:{font_size}"
        )
        return font_size

    def is_card_album(self, image):
        width, height = image.size
        if (
            abs(width - self.default_album_width) <= 20
            and abs(height - self.default_album_height) <= 20
        ):
            return True
        return False

    def func(self, image, all_prompt, text_color, font_path, font_size):
        print(f"input_tensor_image:{image}, type:{type(image)}, shape:{image.shape}")

        image1 = image[0]
        pil_image = tensor_to_pil(image1)
        image_width, image_height = pil_image.size
        if (
            abs(image_width - self.default_album_width) > 20
            or abs(image_height - self.default_album_height) > 20
        ):
            raise Exception("only support bf album image")  # 其他图片需要配置卡牌位置

        if not self.is_card_album(pil_image):
            raise Exception("only support bf album image")
        font_path = font_path or self.default_font_path
        text_color = text_color or "#FFFFFF"
        all_prompt_dict = self.parse_all_prompt_to_dict(all_prompt)
        longest_title = max(all_prompt_dict.values(), key=len)
        if font_size <= 0:
            font_size = self.auto_font_size(longest_title)

        font = ImageFont.truetype(font_path, font_size)
        text_image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_image)

        for i, title in all_prompt_dict.items():
            title = str(title)
            index = int(i)
            index = index + 1
            x, y = self.get_text_pos_by_config(draw, font, index, title)
            print(x, y, title)
            draw.text((x, y), title, font=font, fill=text_color)

        combine_image = Image.alpha_composite(pil_image.convert("RGBA"), text_image)
        print(
            pil_image,
        )
        print(combine_image, combine_image.size)
        combine_image.save(
            "E:\\AI\\ComfyUI_windows_portable_nvidia_cu121_or_cpu\\ComfyUI_windows_portable\\output\\from_tensor_2_{}.png".format(
                int(time.time())
            )
        )

        tensor_image_old = utils.pil_to_tensor_old(combine_image)
        tensor_image = pil_to_tensor(combine_image)
        tensor_image1 = utils.pil_to_tensor1(combine_image)
        old_tensor_image = pil_to_tensor(pil_image)
        old_tensor_image_1 = utils.pil_to_tensor_old(pil_image)
        print(
            tensor_image.shape,
            tensor_image_old.shape,
            tensor_image1.shape,
            old_tensor_image.shape,
            old_tensor_image_1.shape,
        )

        return (
            tensor_image,
            tensor_image_old,
            tensor_image,
            old_tensor_image,
            old_tensor_image_1,
            image1,
        )


class ShowImageInfo(Base):
    RETURN_TYPES = ("STRING", "IMAGE", "INT", "INT")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "title": ("STRING", {"forceInput": False}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    INPUT_IS_LIST = True
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (False, False, False, False)
    RETURN_NAMES = (
        "image_shape",
        "image",
        "width",
        "height",
    )

    def func(self, image, unique_id=None, extra_pnginfo=None, title=""):
        image1 = image[0]
        pil_image = tensor_to_pil(image1)
        size = pil_image.size
        return_size = "{}*{}".format(size[0], size[1])
        # print(return_size, unique_id, extra_pnginfo)
        preview_images = PreviewImage().save_images(image[0])["ui"]["images"]
        if unique_id is not None and extra_pnginfo is not None:
            if not isinstance(extra_pnginfo, list):
                print("Error: extra_pnginfo is not a list")
            elif (
                not isinstance(extra_pnginfo[0], dict)
                or "workflow" not in extra_pnginfo[0]
            ):
                print("Error: extra_pnginfo[0] is not a dict or missing 'workflow' key")
            else:
                workflow = extra_pnginfo[0]["workflow"]
                node = next(
                    (x for x in workflow["nodes"] if str(x["id"]) == str(unique_id[0])),
                    None,
                )
                if node:
                    node["widgets_values"] = [[return_size]]

        return {
            "ui": {
                "images": preview_images,
                "text": [[return_size]],
            },
            "result": (return_size, image1, size[0], size[1]),
        }



class TestImageTransport(Base):
    RETURN_TYPES = ("IMAGE",)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
               
            }
        }

    INPUT_IS_LIST = False
    OUTPUT_NODE = True

    def func(self, image, **kw):
        pil_image = tensor_to_pil(image)
        tensor_img = pil_to_tensor(pil_image)

        return (tensor_img,)

class Test(Base):
    RETURN_TYPES = ("STRING",)
    bg_list = ["name1", "name2", "name3"]

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # "image": ("IMAGE",),
                # "title": ("STRING", {"forceInput": False}),
                "bg": (s.bg_list,)
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    INPUT_IS_LIST = False
    OUTPUT_NODE = True

    def func(self, bg="", **kw):

        logging.info("TestNode, func, bg: {bg}, kw:{kw}")
        return (bg,)


class ShowJsonList(Base):
    # 把一个list的json字符串， 解析成多个字符串展示
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "LIST_JSON": ("STRING", {"multiline": True, "default": "[]"}),
            },
        }

    RETURN_TYPES = (
        "SIMPLE_PROMPT_LIST",
        "STRING",
    )
    RETURN_NAMES = (
        "SIMPLE_PROMPT_LIST",
        "STRING",
    )


class PromptList5(Base):

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_1": ("STRING", {"multiline": True, "default": "prompt1"}),
                "prompt_2": ("STRING", {"multiline": True, "default": "prompt2"}),
                "prompt_3": ("STRING", {"multiline": True, "default": "prompt3"}),
                "prompt_4": ("STRING", {"multiline": True, "default": "prompt4"}),
                "prompt_5": ("STRING", {"multiline": True, "default": "prompt5"}),
                "return_type": (["list", "dict"],),
            },
            "optional": {"prompt_list": ("PROMPT_LIST",)},
        }

    RETURN_TYPES = (
        "PROMPT_LIST",
        "STRING",
    )
    RETURN_NAMES = (
        "prompt_list",
        "json_results",
    )

    def func(
        self,
        prompt_1,
        prompt_2,
        prompt_3,
        prompt_4,
        prompt_5,
        return_type="list",
        prompt_list=None,
    ):

        # Initialise the list
        prompts = list()

        # Extend the list for each prompt in connected stacks
        if prompt_list is not None:
            prompts.extend([l for l in prompt_list])

        # Extend the list for each prompt in the stack
        if prompt_1 != "":
            prompts.extend([(prompt_1)]),

        if prompt_2 != "":
            prompts.extend([(prompt_2)]),

        if prompt_3 != "":
            prompts.extend([(prompt_3)]),

        if prompt_4 != "":
            prompts.extend([(prompt_4)]),

        if prompt_5 != "":
            prompts.extend([(prompt_5)]),

        prompts = [i for i in prompts if i]
        combined_prompts_dict = {str(i): p for i, p in enumerate(prompts)}

        if return_type == "list":
            return (
                prompts,
                json.dumps(prompts, ensure_ascii=False),
            )  # ensure_ascii=False 参数可以防止中文转成unicode, 转成unicode 之后， 翻译节点就不能用了
        else:
            return (
                prompts,
                json.dumps(combined_prompts_dict, ensure_ascii=False, indent=4),
            )


class PromptList2(Base):

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_1": ("STRING", {"multiline": True, "default": "prompt1"}),
                "prompt_2": ("STRING", {"multiline": True, "default": "prompt2"}),
                "return_type": (["list", "dict"],),
            },
            "optional": {"prompt_list": ("PROMPT_LIST",)},
           
            
        }

    RETURN_TYPES = (
        "PROMPT_LIST",
        "STRING",
    )
    RETURN_NAMES = (
        "prompt_list",
        "json_results",
    )

    def func(self, prompt_1, prompt_2, prompt_list=None, return_type="list"):

        # Initialise the list
        prompts = list()

        # Extend the list for each prompt in connected stacks
        if prompt_list is not None:
            prompts.extend([l for l in prompt_list])

        # Extend the list for each prompt in the stack
        if prompt_1 != "":
            prompts.extend([(prompt_1)]),

        if prompt_2 != "":
            prompts.extend([(prompt_2)]),
        prompts = [i for i in prompts if i]
        combined_prompts_dict = {str(i): p for i, p in enumerate(prompts)}
        if return_type == "list":
            return (
                prompts,
                json.dumps(prompts, ensure_ascii=False),
            )  # ensure_ascii=False 参数可以防止中文转成unicode, 转成unicode 之后， 翻译节点就不能用了
        else:
            return (
                prompts,
                json.dumps(combined_prompts_dict, ensure_ascii=False, indent=4),
            )


class ExpandPromot(Base):
    # 扩充midjourney的提示词
    RETURN_TYPES = ("STRING",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_type": (["MD", "SD"],),
                "prompt": ("STRING", {"default": "1girl", "forceInput": True}),
            },
            # "optional": {"prompt": ("STRING",)},
        }

    def func(self, prompt_type, prompt):
        rich_prompt = open_ai_client.expand_prompt(
            user_prompt=prompt, prompt_type=prompt_type
        )
        return (rich_prompt,)


class ExpandPromotBatch(Base):
    # 批量扩充midjourney的提示词,  | 分割的prompt
    RETURN_TYPES = ("STRING",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_type": (["MD", "SD"],),
                "prompt_list_json": ("STRING", {"default": "", "forceInput": True}),
            },
        }

    def func(self, prompt_type, prompt_list_json):
        try:
            prompt_list = json.loads(prompt_list_json)
            print(f"prompt_list:{prompt_list}")
        except Exception as e:
            raise ValueError('input should be a json string, like ["aaa", "bbb"]')
        if not isinstance(prompt_list, list):
            raise ValueError("prompt_list must be a list")
        rich_prompt_list = open_ai_client_async.expand_prompt(
            prompt_list, prompt_type=prompt_type
        )
        rich_prompt_list = [i for i in rich_prompt_list if i]
        print(f"rich_prompt_list:{rich_prompt_list}")
        return (json.dumps(rich_prompt_list, ensure_ascii=False),)


class MDImagine(Base):
    # 使用midjourney 生成图像， 默认选第三张; 建议使用
    RETURN_TYPES = ("STRING", "IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = (
        "url_results",
        "thumbnail",
        "img1",
        "img2",
        "img3",
        "img4",
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                # "image_index": ("INT", {"default": 1, "min": 1, "max": 4, "step": 1}),
                "aspect": ("STRING", {"default": "1:1", "multiline": False}),
                # "size": ("STRING", {"default": "", "multiline": False}),
                "chaos": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "stylize": ("INT", {"default": 100, "min": 0, "max": 1000, "step": 1}),
                # "style": (["raw", "random-32", "random-64", "random-128"],),
                "no": ("STRING", {"default": "", "multiline": False}),
                "niji": ([False, True],),
                # "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295, "step": 1}),
            },
            # "optional": {"prompt": ("STRING",)},
        }
    
    def pack_prompt(self, prompt, aspect, chaos, stylize, no, niji, seed=None):
        if aspect:
            prompt += f" --ar {aspect} "
        if chaos:
            prompt += f" --chaos {chaos} "
        if stylize:
            prompt += f" --s {stylize} "
        # if style:
        #     prompt += f" --style {style} "
        if no:
            prompt += f" --no {no} "
        if niji:
            prompt += f" --niji 6 "
        else:
            prompt += f" --v 6 "

        # if seed:
        #     prompt += f" --seed {seed} "
        
        return prompt

    def func(self, prompt, aspect, chaos, stylize, no, niji):

        if not prompt:
            null_tensor = torch.empty(0)
            return (
                null_tensor, 
                null_tensor,
                null_tensor,
                null_tensor,
            )
        prompt = self.pack_prompt(prompt, aspect, chaos, stylize, no, niji)
        url_results = midjouney_async.get_image(prompt, type="single")
        image_list = utils.image_url_to_tensor(url_results)

        print(f"MDImagine, image_list length: {len(image_list)}")
        return (
                ",".join(url_results),
                image_list[0],
                image_list[1], image_list[2], image_list[3], image_list[4], 
            )



class MDImagineBatch(MDImagine):
    # 使用midjourney 生成图像， 默认选第三张; 建议使用
    RETURN_TYPES = ("STRING", "IMAGE", "IMAGE")
    RETURN_NAMES = (
        "results_url",
        "thumbnails",
        "result_images",
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompts": ("STRING", {"default": '["1girl"]', "multiline": True, "forceInput": True}),
                "image_index": ("INT", {"default": 1, "min": 1, "max": 4, "step": 1}),
                "aspect": ("STRING", {"default": "464:584", "multiline": False}),
                # "size": ("STRING", {"default": "464px*584px", "multiline": False}),
                "chaos": ("INT", {"default": 0, "min": 0, "max": 100, "step": 1}),
                "stylize": ("INT", {"default": 500, "min": 0, "max": 1000, "step": 1}),
                # "style": (["raw", "random-32", "random-64", "random-128"],),
                "no": ("STRING", {"default": "", "multiline": False}),
                "niji": ([False, True],),
                # "seed": ("INT", {"default": 0, "min": 0, "max": 4294967295, "step": 1}),
            },
        }

    def func(self, prompts, image_index, aspect, chaos, stylize, no, niji):
        try:
            prompt_list = json.loads(prompts)
        except Exception as e:
            raise ValueError(f"Could not parse prompts to list: {prompts}")
        prompt_list = [self.pack_prompt(i, aspect, chaos, stylize, no, niji) for i in prompt_list if i]
        if not prompt_list:
            print("error: prompt list is empty in MDImagineBatch！！！")
            return (
                "[]",
                torch.empty(0),
                torch.empty(0),
            )
        url_results = midjouney_async.get_image(prompt_list, image_index, type="batch")
        
        thumbnail_list = utils.image_url_to_tensor(url_results[0])
        images = utils.image_url_to_tensor(url_results[1:])

        return (json.dumps(url_results, ensure_ascii=False), utils.pack_images(thumbnail_list), utils.pack_images(images))


class ShowImageByUrl(Base):
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "", "multiline": True}),
            },
        }

    def func(self, url):
        print(f"start ShowImageByUrl: {url}")
        url_list = url.split(",")
        url_list = [i.strip() for i in url_list]
        url_list = url_list[:1]
        print(f"ShowImageByUrl: {url_list}")
        results = utils.image_url_to_tensor(url_list)
        
        return results[:1]

class ShowImageByUrlBatch(Base):
    RETURN_TYPES = ("IMAGE",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "", "multiline": True}),
            },
        }

    def func(self, url):
        url_list = url.split(",")
        url_list = [i.strip() for i in url_list]
        results = utils.image_url_to_tensor(url_list)
        
        print(f"ShowImageByUrl, len(results): {len(results)}")

        s = utils.pack_images(results)
        
        return [s,]

