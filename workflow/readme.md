
## bf 内部自定义节点说明


### ShowImageInfo
展示图像尺寸，以及预览图像
输入的title 字段可以忽略
输出分别是  图像尺寸 xx*xxx,  原始图像， 图像宽度， 图像高度


### BfNote
查看本文档



### ToString
把 其他数据类型转换成 字符串
输入可以是 字符串， 整型， 浮点型数据
输出：
    SAME AS INPUT: 把输入原样输出
    STRING： 把输入类型转成字符串输出



### PromptList2  或者 PromptList5
组合多个prompt
return_type 支持 list 和 dict 两种， 以输入为 prompt1 和 prompt2 为例 看一下json_results的格式
    list: ["prompt1", "prompt2"]
    dict: {
            "0": "prompt1",
            "1": "prompt2"
        }

prompt_list 是用来串联多个 PromptList2  或者  PromptList5



### ExpandPromot
扩充提示词
支持 midjourney （MD） 和  stable diffusion (SD) 两种模式
输入 prompt  是 字符串

### ExpandPromotBatch
批量扩充提示词
输入prompt_list_json 需要是 ["prompt1", "prompt2"] 这种格式的json字符串， 也就是 PromptList2 选择list模式的 json_results
输出也是 ["prompt1", "prompt2"] 这种格式的json字符串


### MDImagine
使用 midjourney 绘图
输入
    prompt: 提示词 字符串
    image_index: 数字， 选择md 生成图像的第几张放大
输出：
    result_url: 字符串， 生成图片的url地址
    thumbnail： 图像， 缩略图
    result_image: 图像， 根据输入的image_index 对缩略图中的对应图片放大后的图像

### MDImagineBatch
批量 使用 midjourney 绘图
输入：
    prompts: 提示词数组， 需要 ["prompt1", "prompt2"] 这种格式的json字符串

其他与MDImagine 一样
生成的图像是 多张组合在一起的


### ShowImageByUrl
根据网络地址获取图像
输入是一张网络图像的url地址
输出是image 对象


### ShowImageByUrlBatch
ShowImageByUrl 的批量操作
输入    
    url: 逗号分割的多个url




