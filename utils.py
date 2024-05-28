import asyncio
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import PIL as pillow
import torch
import numpy as np

import comfy


def tensor_to_pil(tensor_image):
    print(tensor_image.shape)
    # 移除批量维度，使用 squeeze 或者直接索引
    image_tensor = tensor_image.squeeze(0)  # 如果批量大小为1，squeeze将移除第一个维度

    # 或者使用索引选择单个图像（如果批量大小大于1）
    # image_tensor = tensor_image[0]

    print(image_tensor.dtype)
    if image_tensor.dtype == torch.float32:
        image_tensor = (image_tensor * 255).to(torch.uint8)
        
    elif image_tensor.dtype != torch.uint8:
        # 直接转换为 uint8 而不需要缩放
        image_tensor = image_tensor.to(torch.uint8)
        # tensor = tensor.byte()
        # tensor = tensor.permute(1, 2, 0)  # 从 'C, H, W' 到 'H, W, C'
    pil_image = Image.fromarray(image_tensor.numpy())

    return pil_image

def pil_to_tensor(pil_image):
    tensor_img = torch.from_numpy(np.array(pil_image).astype(np.float32) / 255.0).unsqueeze(0)

    # numpy_image = np.array(pil_image).astype(np.float32) / 255.0
    # tensor_img = torch.from_numpy(numpy_image).permute(2, 0, 1).unsqueeze(0)

    print(f"tensor_img.shape:{tensor_img.shape}")
    return tensor_img

def pil_to_tensor_old(pil_image):
    numpy_image_normalized = np.array(pil_image).astype(np.float32) / 255.0
    #  numpy_image_transposed = np.transpose(numpy_image_normalized, (2, 0, 1))
    numpy_image_transposed = np.transpose(numpy_image_normalized, (2, 0, 1))
    tensor_image = torch.from_numpy(numpy_image_transposed).unsqueeze(0)
    print(tensor_image)
    print(tensor_image.shape)
    return tensor_image

def pil_to_tensor1(pil_image):
    numpy_image_normalized = np.array(pil_image).astype(np.float32) / 255.0
    numpy_image_transposed = np.transpose(numpy_image_normalized, (2, 0, 1))
    tensor_image = torch.from_numpy(numpy_image_transposed).unsqueeze(0)
    return tensor_image


def formated_app_version(app_version):
    return "{:0>3}.{:0>3}.{:0>3}".format(*app_version.split("."))


def get_text_size(draw, font, text):
    if formated_app_version(pillow.__version__) < "010.000.000":
        return draw.textsize(text, font=font)
    else:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        # 计算文本宽度和高度
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        return text_width, text_height


def image_url_to_tensor(url_list):
    
    async def download_image(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()
                img = Image.open(BytesIO(content)).convert('RGB')
                tensor_img = pil_to_tensor(img)
                print(url)
                return tensor_img
            
    async def start():
        tasks = [download_image(url) for url in url_list]
        results = await asyncio.gather(*tasks)
        return results

    return asyncio.run(start())


# 把多张图片的tensor对象拼成一个tensor对象
def pack_images(tensor_images_list):
    if len(tensor_images_list) > 1:
        image0 = tensor_images_list[0]
        for i, img in enumerate(tensor_images_list[1:]):
            print(f"iter img_results, i:{i}, img.shape:{img.shape}, image0.shape:{image0.shape}")
            if img.shape[1:] != image0.shape[1:]:
                tensor_images_list[i+1] = comfy.utils.common_upscale(img.movedim(-1,1), image0.shape[2], image0.shape[1], "bilinear", "center").movedim(1,-1)
    s = torch.cat(tensor_images_list, dim=0)

    return s


    

        

# 提示词列表， cr 插件中也有， 叫 CR Simple Prompt List   https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes 

