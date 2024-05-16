import json
from .utils import tensor_to_pil, pil_to_tensor, get_text_size
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageChops
from . import utils

import time


class Base:

    CATEGORY = "can"
    FUNCTION = "func"
    RETURN_TYPES = ()

class GetTitleByIndex(Base):
    RETURN_TYPES = ("STRING", "INT")
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                
                "all_prompt": ("STRING", {
                    "default": "default_title"
                }),
                "index": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 50,
                    "step": 1
                })
                
            },
        }

    def func(self, all_prompt, index):
        print(all_prompt)
        print(type(all_prompt))

        all_prompt_dict = "{" + all_prompt + "}"
        all_prompt_dict = json.loads(all_prompt_dict)
        title = all_prompt_dict.get(str(index-1)) or "default title"
        return title, index


class AddTitleToImage(Base):
    # 为生成的图片添加title

    RETURN_TYPES= ("IMAGE", "STRING")
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "print_to_screen": (["enable", "disable"],),
                "title": ("STRING", {
                    "default": "default_title"
                }),
                "font_size": ("INT", {
                    "default": -1,
                    "min": -2,
                    "max": 1000,
                    "step": 2,
                    "display": "-1表示自适应"

                }),
                "font_path": ("STRING", {
                    "default": "C:\\Users\\Admin\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Neuron Regular.otf"
                }),
                "text_color": (
                    "STRING", {
                        "default": "#FFFFFF"
                    }
                )
                
            },
        }

    def add_title(self, pil_image, title, text_color=None, font_path=None, font_size=0):
        font_path = font_path or "C:\\Users\\Admin\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Neuron Regular.otf"
        image_width, image_height = pil_image.size
        if font_size <= 0:
            font_size = image_width // 10
        font = ImageFont.truetype(font_path, font_size)
        text_image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    
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



    def func(self, image, title, print_to_screen="enable", font_path=None, font_size=0, text_color=None):
        if print_to_screen == "enable":
            print(f"""Your input contains:
                string_field aka input text: {title}
            """)
        new_str = f"add_title_{title}"
        image1 = image[0]
        pil_image = tensor_to_pil(image1)
        pil_image = self.add_title(pil_image, title, text_color, font_path, font_size)
        pil_image.save("E:\\AI\\ComfyUI_windows_portable_nvidia_cu121_or_cpu\\ComfyUI_windows_portable\\output\\from_tensor_{}.png".format(int(time.time())))

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
                "all_prompt": ("STRING", {
                    "default": "default_title"
                }),
                "font_size": ("INT", {
                    "default": -1,
                    "min": -2,
                    "max": 1000,
                    "step": 2,
                    "display": "-1表示自适应"

                }),
                "font_path": ("STRING", {
                    "default": "C:\\Users\\Admin\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Neuron Regular.otf"
                }),
                "text_color": (
                    "STRING", {
                        "default": "#FFFFFF"
                    }
                )
                
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
            10: (1738, 875)
        }
    
    def get_text_pos_by_config(self, draw, font, index, text):
        
        w, h = self.card_pos_config.get(index) or (0, 0)
        text_width, text_height = get_text_size(draw, font, text)

        text_start_width = w - text_width//2
        text_start_height = h - text_height // 2

        return text_start_width, text_start_height
    
    
    def parse_all_prompt_to_dict(self, all_prompt):
        all_prompt_dict = "{" + all_prompt + "}"
        all_prompt_dict = json.loads(all_prompt_dict)
        return all_prompt_dict
    
    def auto_font_size(self, longest_text):
        font_size = (self.card_width // len(longest_text)) or 1
        print(f"auto font_size, card_width: {self.card_width}, longest_text: {longest_text}, length:{len(longest_text)}, font_size:{font_size}")
        return font_size

    def is_card_album(self, image):
        width, height = image.size
        if abs(width-self.default_album_width) <= 20 and abs(height-self.default_album_height) <= 20:
            return True
        return False

    def func(self, image, all_prompt, text_color, font_path, font_size):
        print(f"input_tensor_image:{image}, type:{type(image)}, shape:{image.shape}")

        image1 = image[0]
        pil_image = tensor_to_pil(image1)
        image_width, image_height = pil_image.size
        if abs(image_width-self.default_album_width) > 20 or abs(image_height-self.default_album_height) > 20:
            raise Exception("only support bf album image")   # 其他图片需要配置卡牌位置

        if not self.is_card_album(pil_image):
            raise Exception("only support bf album image")
        font_path = font_path or self.default_font_path
        text_color = text_color or "#FFFFFF"
        all_prompt_dict = self.parse_all_prompt_to_dict(all_prompt)
        longest_title = max(all_prompt_dict.values(), key=len)
        if font_size <= 0:
            font_size = self.auto_font_size(longest_title)
        
        
        font = ImageFont.truetype(font_path, font_size)
        text_image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_image)

        for i, title in all_prompt_dict.items():
            title = str(title)
            index = int(i)
            index = index+1
            x, y = self.get_text_pos_by_config(draw, font, index, title)
            print(x, y, title)
            draw.text((x, y), title, font=font, fill=text_color)

        combine_image = Image.alpha_composite(pil_image.convert("RGBA"), text_image)
        print(pil_image, )
        print(combine_image, combine_image.size)
        combine_image.save("E:\\AI\\ComfyUI_windows_portable_nvidia_cu121_or_cpu\\ComfyUI_windows_portable\\output\\from_tensor_2_{}.png".format(int(time.time())))

        tensor_image_old = utils.pil_to_tensor_old(combine_image)
        tensor_image = pil_to_tensor(combine_image)
        tensor_image1 = utils.pil_to_tensor1(combine_image)
        old_tensor_image = pil_to_tensor(pil_image)
        old_tensor_image_1 = utils.pil_to_tensor_old(pil_image)
        print(tensor_image.shape, tensor_image_old.shape, tensor_image1.shape, old_tensor_image.shape, old_tensor_image_1.shape )
        
        return tensor_image, tensor_image_old,  tensor_image,  old_tensor_image, old_tensor_image_1, image1
        
