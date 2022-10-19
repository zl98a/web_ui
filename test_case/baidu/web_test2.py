import sys
import time
import traceback

import json

sys.path.append(r'C:\pythonPro\web_ui')
from base.config import init_page, rootPath
from base.config import read_yaml, packing_parameters2, report_email, read_yaml2, query_case
from base.base_page import BasePage, get_driver


class Case(object):
    def __init__(self, case_file=None, element_file=None):
        self.filename = case_file  # 用例文件
        self.element_file = element_file  # 元素文件
        self.driver = BasePage(get_driver(None))
        self.index = 1
        self.case_results_list = []  # 用例列表
        self.case_results_dict = {}  # 用例执行结果统计
        # 可以在初始化阶段登录
        self.exception_flag = False  # 报错标识

    # 定义三个操作函数, 并保持参数签名统一
    def do_open(self, target, value=None, wait_time=None):
        print('打开页面', target)
        self.driver.open(target)

    def do_type(self, target=None, value=None, wait_time=None):
        print(f'在 {target} 输入 {value}')
        self.driver.input(loc=target, txt=value)

    def do_click(self, target, value=None, wait_time=None):
        print(f'点击 {target}')
        self.driver.click(target)

    def do_back(self, target, value=None, wait_time=None):
        print('执行了返回操作。')
        self.driver.by_back()  # 返回

    def do_swipe(self, target, value=None, wait_time=None):
        print('滑动屏幕查找某个元素')
        find_ele = self.driver.pub_swipe_down(elm_loc=target)
        if not find_ele:
            print('没找到元素。')
            assert False
        try:
            self.driver.execute_javascript(find_ele)
        except Exception as e:
            print(e)

    def print_page_source(self, target, value=None, wait_time=None):
        print('打印页面源码')
        print(self.driver.page_source)

    def wait_time(self, target=None, value=None, wait_time=None):
        print('强制等待.....')
        time.sleep(wait_time)

    def jump_window_1(self, target, value=None, wait_time=None):
        self.driver.jump_handles()

    def jump_window_0(self, target, value=None, wait_time=None):
        try:
            self.driver.jump_handles(0)
        except:
            pass

    def close_current_window(self, target, value=None, wait_time=None):
        self.driver.close_()  # 关闭当前浏览器窗口

    # 使用字典做动作映射
    command_map = {
        'open': do_open,  # 上面定义的do_open函数
        'type': do_type,  # 上面定义的do_type函数
        'click': do_click,  # 上面定义的do_click函数
        'back': do_back,  # 返回
        'swipe': do_swipe,  # 滑动屏幕
        'print': print_page_source,
        'wait': wait_time,
        'jump_window_1': jump_window_1,
        'jump_window_0': jump_window_0,
        'close_current_window': close_current_window
    }

    def run_case(self, file, many=None):
        data = read_yaml(file)  # 读取所有测试用例
        res = self.execute_case(data, many=many)  # 执行用例
        return res

    def execute_case(self, data, many=None):
        # 执行用例
        for item in data:  # 遍历用例【所有的用例】
            if many:
                item2 = data.get(many['case_module'])
            else:
                item2 = data.get(item)  # 首页-百度搜索
            for item3 in item2:  # 遍历模块多个用例
                if many:
                    item3 = many['case_name']  # 获取单条用例
                self.do_open(target=init_page)  # 每次执行新用例前，先回到到首页
                print(f'正在执行的用例为:【{item3}】')
                self.case_results_dict['name'] = item3  # 用例名称
                elements = read_yaml2(self.element_file)
                if many:
                    col = many['case_module']
                else:
                    col = item
                element = query_case(elements, col=col)
                # 如果该用例对其他页面元素产生依赖，处理如下
                case_ = item2.get(item3)  #
                case_process_list = []  # 用例处理流程
                self.case_results_dict['执行步骤'] = str(case_)
                for step in case_:  # 循环遍历用例执行步骤
                    step = self.deal_parameters_depend(element_dic=step, default_element_dic=element)
                    command, target, value, wait_time = packing_parameters2(step)
                    func = self.command_map.get(command)
                    self.case_results_dict['执行命令'] = command  # 用例执行命令
                    self.case_results_dict['操作元素'] = target  # 操作元素
                    self.case_results_dict['输入值'] = value  # 输入值
                    try:
                        func(self, target=target, value=value, wait_time=wait_time)  # 执行函数
                    except Exception as e:
                        print(e)
                        verify_res, keyword = self.keyword_verify(step)  # 接收检验结果
                        error_info = traceback.format_exc()
                        self.case_results_dict['报错信息'] = str(error_info)+"\n"+str(step)
                        self.case_results_dict['运行结果'] = '失败'
                        self.case_results_dict['报错步骤'] = str(step)
                        self.case_results_dict['校验结果'] = (lambda x: '成功' if x == 'True' else '失败')(verify_res)
                        self.case_results_dict['校验关键字'] = keyword
                        # 失败重跑
                        self.exception_flag = True
                    else:
                        verify_res, keyword = self.keyword_verify(step)  # 接收检验结果
                        self.case_results_dict['运行结果'] = '成功'
                        self.case_results_dict['报错信息'] = '无'
                        self.case_results_dict['报错步骤'] = '无'
                        self.case_results_dict['校验关键字'] = keyword
                        self.case_results_dict['校验结果'] = (lambda x: '成功' if x == 'True' else '失败')(verify_res)
                        self.exception_flag = False  # 还原，无报错
                    case_process_list.append(json.dumps(self.case_results_dict, ensure_ascii=False))
                    time.sleep(0.5)  # 每个用例执行完毕后，等待3s
                    if self.exception_flag:
                        break
                self.case_results_list.append(case_process_list)  # 添加运行结果到列表里
                if many:  # 执行单条用例
                    return self.case_results_list
        return self.case_results_list

    def keyword_verify(self, step):
        """关键字校验函数"""
        page_source = None
        try:
            page_source = self.driver.page_source()
        except Exception as e:
            print(e)
        item = None
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
            if isinstance(item, str) or isinstance(item, int):  # 参数为字符串 或 整型
                if str(item) in page_source:
                    verify_res.append({item: 'True'})
                else:
                    verify_res.append({item: 'False'})
        results = []  # 最终结果
        for item in verify_res:
            for k, v in item.items():
                results.append(f'{k}={v}')

        if 'False' in str(verify_res):
            return 'False', ''.join(results)
        else:
            return 'True', ''.join(results)

    def deal_parameters_depend(self, element_dic=None, default_element_dic=None):
        """封装参数"""
        try:  # 处理用例依赖
            depend = element_dic['depend']  # 用例之间有依赖
        except Exception as e:  # 没有依赖
            print(e)
        else:  # 处理依赖
            elements = read_yaml2(self.element_file)
            element = elements.get(depend)
            del element_dic['depend']  # 局部删除，不会影响文档里的该字段
            element_dic = self.deal_parameters_depend(element_dic, element)
        # 用例组装
        for k, v in element_dic.items():  # {'command': 'type', 'target': 'id=关键字输入框', 'value': '双12'}
            for k2, v2 in default_element_dic.items():  # {'关键字输入框': 'id=kw', '提交按钮': 'id=su'}
                try:
                    if k2 == v:
                        element_dic[k] = v2
                except Exception as e:
                    print(e)
        return element_dic

    def run(self, many=None, report=True):
        """总调度方法"""
        items = self.run_case(self.filename, many=many)  # 返回执行结果
        self.driver.quit_()
        report_email(items, report)
