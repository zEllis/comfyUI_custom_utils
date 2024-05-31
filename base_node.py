
from .components.fields import Field

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


ANY = AnyType("*")


class Base:

    CATEGORY = "bf"
    FUNCTION = "func"
    RETURN_TYPES = ()


class Tools:

    CATEGORY = "bf/tools"
    FUNCTION = "func"
    RETURN_TYPES = ()


class ToString(Tools):

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ANY": Field.any(),
            },
        }

    RETURN_TYPES = (
        ANY,
        "STRING",
    )
    RETURN_NAMES = (
        "SAME AS INPUT",
        "STRING",
    )
    OUTPUT_NODE = True
    FUNCTION = "func"

    def func(self, ANY=None):
        out = ANY
        try:
            out = str(out)
        except Exception as e:
            out = str(e)
        return {"ui": {"text": [out]}, "result": (ANY, out)}


class Text(Tools):
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)

    @classmethod
    def INPUT_TYPES(cls): 
        return {
                "required": {
                    "text": ("STRING", {"default": "", "multiline": True}),
                }
        }

    def func(self, text):

        return (
            text,
        )


