from PIL import Image, ImageDraw, ImageFont
import PIL as pillow
import torch
import numpy as np


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

def pil_to_tensor_old(pil_image):
    return torch.from_numpy(np.array(pil_image).astype(np.float32) / 255.0).unsqueeze(0)

def pil_to_tensor(pil_image):
    numpy_image_normalized = np.array(pil_image).astype(np.float32) / 255.0
    #  numpy_image_transposed = np.transpose(numpy_image_normalized, (2, 0, 1))
    numpy_image_transposed = np.transpose(numpy_image_normalized, (2, 0, 1))
    tensor_image = torch.from_numpy(numpy_image_transposed).unsqueeze(0)
    
    return tensor_image

def pil_to_tensor1(pil_image):
    numpy_image_normalized = np.array(pil_image).astype(np.float32) / 255.0
    #  numpy_image_transposed = np.transpose(numpy_image_normalized, (2, 0, 1))
    numpy_image_transposed = np.transpose(numpy_image_normalized, (2, 0, 1))
    tensor_image = torch.from_numpy(numpy_image_transposed).unsqueeze(0)
    tensor_image = tensor_image.permute(0, 2, 3, 1)
    return tensor_image[0]


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
