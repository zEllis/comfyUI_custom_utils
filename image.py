import datetime
import json
import numpy as np
import os
import comfy
from comfy.cli_args import args
import torch

from .base_node import Base
from folder_paths import output_directory, get_save_image_path
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageChops
from PIL.PngImagePlugin import PngInfo


MAX_RESOLUTION=16384

def resize_mask(mask, shape):
    return torch.nn.functional.interpolate(mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])), size=(shape[0], shape[1]), mode="bilinear").squeeze(1)


class ImageNode(Base):
    CATEGORY = "bf/image"

    def check_empty_image(self, image):
        if hasattr(image, "numel") and image.numel() == 0:
            print(f"image is empty")
            return torch.empty(0)
        return None

class bfSaveImage(ImageNode):
    # 比自带的saveImage 多了一个空对象的判断
    def __init__(self):
        self.output_dir = output_directory
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {"required": 
                    {"images": ("IMAGE", ),
                     "filename_prefix": ("STRING", {"default": "ComfyUI"})},
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    def func(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):

        # 需要对日期格式做一下处理
        filename_prefix = filename_prefix.replace("%date:yyyy-MM-dd%", datetime.datetime.now().date().isoformat())
        
        return_empty_image = self.check_empty_image(images)
        if return_empty_image is not None:
            return (return_empty_image, )

        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for (batch_number, image) in enumerate(images):
            if image.numel() == 0:
                print(f"bf save_image, but image is empty, batch_number:{batch_number}")
                continue
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results } }



class bfImageScale(ImageNode):
    
    upscale_methods = ["nearest-exact", "bilinear", "area", "bicubic", "lanczos"]
    crop_methods = ["disabled", "center"]

    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "image": ("IMAGE",), "upscale_method": (s.upscale_methods,),
                              "width": ("INT", {"default": 512, "min": 0, "max": MAX_RESOLUTION, "step": 1}),
                              "height": ("INT", {"default": 512, "min": 0, "max": MAX_RESOLUTION, "step": 1}),
                              "crop": (s.crop_methods,)}}
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"

    def upscale(self, image, upscale_method, width, height, crop):
        return_empty_image = self.check_empty_image(image)
        if return_empty_image is not None:
            return (return_empty_image, )
        
        if width == 0 and height == 0:
            s = image
        else:
            samples = image.movedim(-1,1)

            if width == 0:
                width = max(1, round(samples.shape[3] * height / samples.shape[2]))
            elif height == 0:
                height = max(1, round(samples.shape[2] * width / samples.shape[3]))

            s = comfy.utils.common_upscale(samples, width, height, upscale_method, crop)
            s = s.movedim(1,-1)
        return (s,)


class bfJoinImageWithAlpha(ImageNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
                "required": {
                    "image": ("IMAGE",),
                    "alpha": ("MASK",),
                }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "join_image_with_alpha"

    def join_image_with_alpha(self, image: torch.Tensor, alpha: torch.Tensor):
        return_empty_image = self.check_empty_image(image)
        if return_empty_image is not None:
            return (return_empty_image, )

        batch_size = min(len(image), len(alpha))
        out_images = []

        alpha = 1.0 - resize_mask(alpha, image.shape[1:])
        for i in range(batch_size):
           out_images.append(torch.cat((image[i][:,:,:3], alpha[i].unsqueeze(2)), dim=2))

        result = (torch.stack(out_images),)
        return result
