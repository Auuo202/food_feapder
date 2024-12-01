import json

data = {
    # 模式：0：静态，1：动态
    "model": 1,
    # url的名称
    "name": "测试动态链接",
    # 第一层的url，即获取到链接数据的url
    "url": "http://www.wuxi.gov.cn/zfxxgk/szfxxgkml/zdmsxx/spaq/spjdcjxx/index.shtml",
    # 动态使用，js加载等待时间，单位毫秒
    "waitTime": 5000,
    # 第一层的url的html结果，提取标题标签 - 下面为获取结果中所有a标签下的href中的数据
    "class": "a",
    # 第一层的url的html结果，过滤的attribute - 接着上面的class参数，下面为获取的a标签的title进行过滤
    "attributeKey": "title",
    # 接着attributeKey的过滤值，包含抽检字段的所有值抽取出来
    "attributeKeyContains": "抽检",
    # 文件类型: 默认空，获取xls和xlsx, 后续支持填写excel或word或pdf或zip等，目前系统只支持excel的落库逻辑，其他格式后续开发，具体实现是将其他格式转换为excel，然后用现有逻辑处理
    "fileForm": "",
    # 文件开始行, 表头所在的行 - 1，请看下面的解释
    "fileStartLine": 2
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

#
# with open('/Users/auuo/ff_test/feapder/food/data.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)
# print(data)
# item = dict(data)
#
# attribute_key_contains = item['attributeKeyContains']
# print(attribute_key_contains)
#
# print('----------------------------')
# a_title_string = "食品抽检"
# print(re.findall(attribute_key_contains, a_title_string))