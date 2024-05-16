from .image_utils import ShowImageInfo, AddTitleToAlbum, BfNote, Test, ToString

# NODE_CLASS_MAPPINGS = {
#      "ShowImageInfo": ShowImageInfo,
#      "ShowText": ShowText
#      }

NODE_CLASS_MAPPINGS = {
    "ShowImageInfo": ShowImageInfo,
    "AddTitleToAlbum": AddTitleToAlbum,
    "BfNote": BfNote, 
    "Test": Test,
    "ToString": ToString
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ShowImageInfo|bf_utils": "bf_utils|image_info",
}


WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

