# encoding=utf-8
import time
import traceback

from selenium.webdriver.support.wait import WebDriverWait
import yaml
from selenium import webdriver

case_results_list = []  # 用例列表
case_results_dict = {}  # 用例执行结果统计
wait = None
import json
from jinja2 import Environment, FileSystemLoader
from base.email_ import mail  # 发送邮件
import os
import datetime
from base.config import rootPath as root_path

def main():
    global wait
    driver = webdriver.Edge(executable_path='../../base/web/msedgedriver.exe')
    # 设置等待
    wait = WebDriverWait(driver, 5, 0.5)
    # 使用匿名函数
    # wait.until(lambda diver: driver.find_element_by_id('kw'))
    driver.maximize_window()
    yaml_file = 'usecase/yaml_case.yaml'
    items = run_yaml(driver, yaml_file)  # 返回执行结果
    driver.quit()
    report_email(items)


# 定义三个操作函数, 并保持参数签名统一
def do_open(dr, target, value=None):
    print('打开页面', target)
    dr.get(target)


def do_type(dr, target, value=None):
    print(f'在 {target} 输入 {value}')
    elm_loc = target.split('=', 1)  # 分割得到定位方式和定位器
    wait_element(dr, elm_loc).send_keys(value)


def wait_element(dr, elm_loc):
    wait.until(lambda dr: dr.find_element(*elm_loc))
    return dr.find_element(*elm_loc)  # 返回元素


def do_click(dr, target, value=None):
    print(f'点击 {target}')
    elm_loc = target.split('=', 1)
    # wait.until(lambda dr: dr.find_element(*elm_loc))
    # dr.find_element(*elm_loc).click()
    wait_element(dr, elm_loc).click()

def do_back(dr, target, value=None):
    print('执行了返回操作。')
    dr.back()  # 返回


# 使用字典做动作映射
command_map = {
    'open': do_open,  # 上面定义的do_open函数
    'type': do_type,  # 上面定义的do_type函数
    'click': do_click,  # 上面定义的do_click函数
    'back': do_back # 返回
}


def run_yaml(dr, file):
    with open(file, encoding='utf-8') as f:
        data = yaml.safe_load(f)
        res = execute_case(dr, data)  # 执行用例
    return res


def execute_case(dr, data):
    # 执行用例
    for item in data:  # 遍历用例
        item2 = data.get(item)  # 首页-百度搜索
        for item3 in item2:
            do_open(dr, target='https://baidu.com')  # 每次执行用例前，先初始化到首页
            print(f'正在执行的用例为:【{item3}】')
            case_results_dict['name'] = item3  # 用例名称
            elements = get_element('elements/baidu_elements.yaml')
            try:
                element = [ele for ele in elements if ele == item][0]
            except Exception as e:
                print(e)
                element = [ele for ele in elements if ele in item][0]
            element = elements[element]  # {'关键字输入框': 'id=kw', '提交按钮': 'id=su'}
            # 如果该用例对其他页面元素产生依赖，处理如下
            case = item2.get(item3)  # p
            case_process_list = []  # 用例处理流程
            for step in case:  # 循环遍历用例执行步骤
                step = packing_parameters(element_dic=step, default_element_dic=element)
                command, target, value = packing_parameters2(step)
                func = command_map.get(command)
                case_results_dict['执行命令'] = command  # 用例执行命令
                case_results_dict['操作元素'] = target  # 操作元素
                case_results_dict['输入值'] = value  # 输入值
                flag = True
                try:
                    # 执行函数
                    func(dr, target, value)
                except Exception as e:
                    print(e)
                    error_info = traceback.format_exc()
                    case_results_dict['报错信息'] = str(error_info)
                    case_results_dict['运行结果'] = '失败'
                    flag = False
                else:
                    case_results_dict['运行结果'] = '成功'
                    case_results_dict['报错信息'] = '无'
                    verify_res, keyword = keyword_verify(step, dr)  # 接收检验结果
                    case_results_dict['校验关键字'] = keyword
                    case_results_dict['校验结果'] = (lambda  x: '成功' if x=='True' else '失败')(verify_res)

                case_process_list.append(json.dumps(case_results_dict, ensure_ascii=False))
                time.sleep(0.5)  # 每个用例执行完毕后，等待3s
                if not flag:  # 报错了， 退出这个流程
                    break
                    # continue
            case_results_list.append(case_process_list)  # 添加运行结果到列表里
    return case_results_list

def keyword_verify(step, dr):
    """关键字校验函数"""
    try:
        item = step['keyword_verify']
    except:
        return 'True', 'None'
    else:
        if str(item) not in dr.page_source:
            print('校验失败')
            return 'False', str(item)
        else:
            return 'True', str(item)

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


def packing_parameters(element_dic=None, default_element_dic=None):
    """封装参数"""
    try:   # 处理用例依赖
        depend = element_dic['depend']  # 用例之间有依赖
    except Exception as e:  # 没有依赖
        pass
    else:  # 处理依赖
        elements = get_element('elements/baidu_elements.yaml')
        element = elements.get(depend)
        del element_dic['depend']  # 局部删除，不会影响文档里的该字段
        element_dic = packing_parameters(element_dic, element)
    # 用例组装
    for k, v in element_dic.items():  # {'command': 'type', 'target': 'id=关键字输入框', 'value': '双12'}
        for k2, v2 in default_element_dic.items():  # {'关键字输入框': 'id=kw', '提交按钮': 'id=su'}
            try:
                if k2 == v:
                    element_dic[k] = v2
            except Exception as e:
                print(e)
    return element_dic


def get_element(file):
    """获取元素"""
    with open(file) as f:
        return yaml.safe_load(f)


def report_email(items):
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
            r = {"case_name": item2['name'], 'result': run_result, 'verify_keyword':item2['校验关键字'], 'error_info': item2['报错信息']}
            items_result.append(r)
    items_result = deleteDuplicate(items_result)
    failed_number = len([item for item in items_result if item['result'] == '失败'])
    successful_number = len([item for item in items_result if item['result'] == '成功'])

    results.update({'标题': '测试报告',
                    '测试时间': datetime.datetime.now().strftime('%Y_%m_%d %H：%M：%S'),
                    '用例总数': case_number,
                    '成功数': successful_number,
                    '成功率': successful_number/case_number*100,
                    '失败数': failed_number,
                    '失败率': failed_number/case_number*100,
                    'items': items_result})

    # 模板文件
    template = Environment(loader=FileSystemLoader(os.path.join(root_path, 'base/web'))).get_template(
        'template.html')  # 查找模板文件
    # 报告路径
    report_path = os.path.join(root_path, 'report/'+datetime.datetime.now().strftime('%Y_%m_%d')+'.html')
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
    if failed_number>0:
        # 发送邮件
        mail(filepath=report_path, log=report_path)  # 发送邮件
    else:
        print('用例执行全部通过。')



def deleteDuplicate(li):
    """列表-字典去重"""
    temp_list = list(set([str(i) for i in li]))
    li = [eval(i) for i in temp_list]
    print('len:', len(li))
    for i in range(len(li)):
        for j in range(i+1, len(li)):
            try:
                if li[i]['case_name'] == li[j]['case_name']:
                    if li[i]['result'] != '成功' and li[i] !='无':
                        li.remove(li[j])
                    elif li[j]['result'] != '成功' and li[j] !='无':
                            li.remove(li[i])
            except Exception as e:
                print(e)
                pass
    return li


# 测试一下
if __name__ == "__main__":
    main()
