import os

from .base_node import Base


my_dir = os.path.dirname(os.path.abspath(__file__))


class BfImageNote(Base):
    @classmethod
    def INPUT_TYPES(cls):
        filepath = os.path.join(my_dir, "workflow", "readme.md")
        with open(filepath, "r", encoding="utf-8") as file:
            examples = file.read()
        return {
            "required": {
                "readme": ("STRING", {"default": examples, "multiline": True}),
            },
        }

    RETURN_TYPES = ()


class MDImagineNote(Base):
    @classmethod
    def INPUT_TYPES(cls):
        note = """image_index: 数字， 选择md 生成图像的第几张放大， md默认生成4张图， 默认选择第一张
aspect: 图像尺寸
chaos: 控制图片生成混乱度，越高图片越多样，越低图片变化越少, 默认0， 取值0-100
stylize: 调节图片艺术化程度，越高越艺术，越低越匹配， 默认500， 取值 0-1000
no:  强制去除图片中元素
niji: niji是一种动画风格模型, 是否启用该模型
"""
        return {
            "required": {
                "readme": ("STRING", {"default": note, "multiline": True}),
            },
        }

    RETURN_TYPES = ()



