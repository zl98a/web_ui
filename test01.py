page_source = """

this is a good thing vm哈哈哈数据接口

"""


def keyword_verify(step):
    verify_res = []
    try:
        item = step['keyword_verify']
    except Exception as e:
        print(e)
        return 'True', 'None'
    else:  #
        if isinstance(item, list):  # 参数为列表
            for ele in item:
                if ele in page_source:
                    verify_res.append({ele: 'True'})
                else:
                    verify_res.append({ele: 'False'})
        if isinstance(item, str):  # 参数为字符串
            if item in page_source:
                verify_res.append({item: 'True'})
            else:
                verify_res.append({item: 'False'})
    return verify_res


# print(keyword_verify({'keyword_verify': '123'}))
# for i in range(5):
# try:
#     if str(item) not in page_source:
#         print(f'{str(item)}校验失败')
#         time.sleep(1)  # 等待1s继续查找
#         if i == 4:
#             return 'False', str(item)
#     else:
#         return 'True', str(item)  # 返回&&跳出循环
# except Exception as e:
#     print(e)
#     return 'False', str(item)
results = []
for item in [{'美文阅读': 'True'}, {'散文123': 'False'}]:
    for k, v in item.items():
        results.append(f'{k}={v}')

print(results)