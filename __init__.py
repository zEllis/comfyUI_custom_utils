from .image_utils import *
from .note import *
from .base_node import *
from .image import *


NODE_CLASS_MAPPINGS = {
    "ShowImageInfo": ShowImageInfo,
    "AddTitleToImage": AddTitleToImage,
    # "TestImageTransport": TestImageTransport,
    "BfImageNote": BfImageNote, 
    "MDImagineNote": MDImagineNote, 
    # "Test": Test,
    "PromptList2": PromptList2,
    "PromptList5": PromptList5,
    "ExpandPromot": ExpandPromot,
    "ExpandPromotBatch": ExpandPromotBatch,
    "MDImagine": MDImagine,
    "MDImagineBatch": MDImagineBatch,
    "GetImageByUrl": GetImageByUrl,
    # "ShowImageByUrlBatch": ShowImageByUrlBatch,

    # tools
    "bfText": bfText,
    "ToString": ToString,

    # image
    "bfSaveImage": bfSaveImage,
    "bfImageScale": bfImageScale,
    "bfJoinImageWithAlpha": bfJoinImageWithAlpha,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ShowImageInfo|bf_utils": "bf_utils|image_info",
    "MDImagineyBatch": "MDImaginey_batch",
}


WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

