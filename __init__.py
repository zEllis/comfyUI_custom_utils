from .image_utils import *

# NODE_CLASS_MAPPINGS = {
#      "ShowImageInfo": ShowImageInfo,
#      "ShowText": ShowText
#      }

NODE_CLASS_MAPPINGS = {
    "ShowImageInfo": ShowImageInfo,
    "AddTitleToImage": AddTitleToImage,
    "TestImageTransport": TestImageTransport,
    "BfNote": BfNote, 
    "Test": Test,
    "ToString": ToString,
    "PromptList2": PromptList2,
    "PromptList5": PromptList5,
    "ExpandPromot": ExpandPromot,
    "ExpandPromotBatch": ExpandPromotBatch,
    "MDImagine": MDImagine,
    "MDImagineBatch": MDImagineBatch,
    "ShowImageByUrl": ShowImageByUrl,
    "ShowImageByUrlBatch": ShowImageByUrlBatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ShowImageInfo|bf_utils": "bf_utils|image_info",
    "MDImagineyBatch": "MDImaginey_batch",
}


WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

