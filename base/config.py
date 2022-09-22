import os
import yaml
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = curPath[:curPath.find("web_ui\\") + len("web_ui\\")]
init_page = 'https://baidu.com'
import json
from jinja2 import Environment, FileSystemLoader
from base.email_ import mail
import datetime

def deleteDuplicate(li):
    """列表-字典去重"""
    temp_list = list(set([str(i) for i in li]))
    li = [eval(i) for i in temp_list]
    flag_list = []
    for i in range(len(li)):
        for j in range(i + 1, len(li)):
            if li[i]['case_name'] == li[j]['case_name']:
                flag_list.append(li[i])
                flag_list.append(li[j])

    tmp_case_list2 = []  # 添加用例名到新列表
    for d in flag_list:
        tmp_case_list2.append(d['case_name'])
    no_repeat_case_list = []  # 存放去重后的列表
    for case_name in list(set(tmp_case_list2)):
        repeat_case = [x for index, x in enumerate(flag_list) if
                       {k: v for k, v in x.items() if (k == "case_name" and v == case_name)}]

        flag = [item for item in repeat_case if item['verify_keyword'] != 'None']
        error_info_case = [item for item in repeat_case if item['error_info'] != '无']
        if flag and error_info_case:
            verify_keyword_list = list(set([(item['verify_keyword'], item['result']) for item in flag]))
            flag[0]['verify_keyword'] = str(verify_keyword_list)
            flag[0]['error_info'] = error_info_case[0]['error_info']
            flag[0]['result'] = '失败'
            no_repeat_case_list.append(flag[0])
        elif not flag and error_info_case:
            repeat_case[0]['verify_keyword'] = 'None'
            repeat_case[0]['error_info'] = error_info_case[0]['error_info']
            repeat_case[0]['result'] = '失败'
            no_repeat_case_list.append(repeat_case[0])
        elif flag and not error_info_case:
            verify_keyword_list = list(set([(item['verify_keyword'], item['result']) for item in flag]))
            flag[0]['verify_keyword'] = str(verify_keyword_list)
            if '失败' in str(verify_keyword_list):
                flag[0]['result'] = '失败'
            else:
                flag[0]['result'] = '成功'
            no_repeat_case_list.append(flag[0])
        else:  # 没有做校验
            tmp_failed_case = None
            if not error_info_case:
                tmp_failed_case = repeat_case[0]
                tmp_failed_case['result'] = '成功'
            if error_info_case:
                tmp_failed_case = repeat_case[0]
                tmp_failed_case['result'] ='失败'
            # for case_ in repeat_case:
            #     if case_['error_info'] != '无':
            #         tmp_failed_case = case_
            #         break
            #     elif case_['result'] =='失败':
            #         tmp_failed_case = case_
            #         break
            #     elif case_['result'] =='成功':
            #         tmp_failed_case = case_
            #         break
            no_repeat_case_list.append(tmp_failed_case)

    for tmp_case_name in tmp_case_list2:
        for d_tmp in li:
            if d_tmp['case_name'] == tmp_case_name:
                li.remove(d_tmp)

    new_results_itme = li + no_repeat_case_list
    return new_results_itme

def read_yaml(file, encoding='utf-8'):
    """读取yaml"""
    data=None
    with open(file, 'r', encoding=encoding) as f:
        return yaml.safe_load(f)

def read_yaml2(file, encoding='gbk'):
    """读取yaml"""
    data=None
    with open(file, 'r', encoding=encoding) as f:
        return yaml.safe_load(f)

def packing_parameters2(step):
    """分装参数"""
    try:
        command = step.get('command')
    except:
        raise
    try:
        target = step.get('target')
    except:
        raise
    try:
        value = step.get('value')
    except:
        raise
    return command, target, value

def report_email(items, report=None):
    """生成报告和发送邮件"""
    case_number = len(items)  # 用例条数
    results = {}
    items_result = []
    for item in items:
        for item2 in item:
            item2 = json.loads(item2)
            # 校验结果校对
            run_result = None  # 运行及结果
            if item2['校验结果']=='成功' and item2['运行结果']=='成功':
                run_result = '成功'
            elif item2['校验结果']=='成功' or item2['运行结果']=='失败':
                run_result = '失败'
            elif item2['校验结果'] == '失败' or item2['运行结果'] == '成功':
                run_result = '失败'
            r = {"run_step": item2['执行步骤'], "case_name": item2['name'], 'result': run_result, 'verify_keyword':item2['校验关键字'], 'error_info': item2['报错信息']}
            items_result.append(r)
    items_result = deleteDuplicate(items_result)
    failed_number = len([item for item in items_result if item['result'] == '失败'])
    successful_number = len([item for item in items_result if item['result'] == '成功'])
    case_list_ = []
    case_numbers = list(range(1, len(items_result) + 1))
    a_list = list(zip(case_numbers, items_result))
    for a in a_list:
        a[1].update({'number': a[0]})
        case_list_.append(a[1])

    results.update({'标题': '测试报告',
                    '测试时间': datetime.datetime.now().strftime('%Y_%m_%d %H：%M：%S'),
                    '用例总数': case_number,
                    '成功数': successful_number,
                    '成功率': successful_number/case_number*100,
                    '失败数': failed_number,
                    '失败率': failed_number/case_number*100,
                    'items': case_list_})

    # 模板文件
    template = Environment(loader=FileSystemLoader(os.path.join(rootPath, 'base/web'))).get_template(
        'template.html')  # 查找模板文件
    # 报告路径
    report_path = os.path.join(rootPath, 'report/'+datetime.datetime.now().strftime('%Y_%m_%d')+'.html')
    with open(os.path.join(report_path), 'w+', encoding='utf-8') as f:
        out = template.render(
            title=results['标题'],
            test_time=results['测试时间'],
            total_case=results['用例总数'],
            items=results['items'],
            successful_number=results['成功数'],
            successful_number_rate = results['成功率'],
            failed_number_rate=results['失败率'],
            failed_number=results['失败数'],
        )
        f.write(out)
        f.close()
    if failed_number>0 and report:
        # 发送邮件
        mail(filepath=report_path, log=report_path)  # 发送邮件
    elif failed_number == 0:
        print('用例执行全部通过。')
    elif not report:
        print('当前为不发邮件配置，请在报告目录下查看运行报告文件。')

def query_case(elements, col):
    try:
        element = [ele for ele in elements if ele == col][0]
    except Exception as e:
        print(e)
        element = [ele for ele in elements if ele in col][0]

    element = elements[element]  # {'关键字输入框': 'id=kw', '提交按钮': 'id=su'}
    return element

