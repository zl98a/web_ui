import time
import traceback

from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver

case_results_list = []  # 用例列表
case_results_dict = {}  # 用例执行结果统计
import json

from base.config import init_page
from base.config import read_yaml, packing_parameters2, report_email, read_yaml2, query_case


class Case(object):
    def __init__(self, case_file=None, element_file=None):
        self.filename = case_file  # 用例文件
        self.element_file = element_file  # 元素文件
        self.driver = webdriver.Edge(executable_path='../../base/web/msedgedriver.exe')
        # 设置等待
        self.wait = WebDriverWait(self.driver, 5, 0.5)
        self.driver.maximize_window()
        self.index = 1

    # 定义三个操作函数, 并保持参数签名统一
    def do_open(self, target, value=None):
        print('打开页面', target)
        self.driver.get(target)

    def do_type(self, target, value=None):
        print(f'在 {target} 输入 {value}')
        elm_loc = target.split('=', 1)  # 分割得到定位方式和定位器
        self.wait_element(elm_loc).send_keys(value)

    def wait_element(self, elm_loc):
        self.wait.until(lambda driver: driver.find_element(*elm_loc))
        return self.driver.find_element(*elm_loc)  # 返回元素

    def do_click(self, target, value=None):
        print(f'点击 {target}')
        elm_loc = target.split('=', 1)
        self.wait_element(elm_loc).click()

    def do_back(self, target, value=None):
        print('执行了返回操作。')
        self.driver.back()  # 返回

    # 使用字典做动作映射
    command_map = {
        'open': do_open,  # 上面定义的do_open函数
        'type': do_type,  # 上面定义的do_type函数
        'click': do_click,  # 上面定义的do_click函数
        'back': do_back  # 返回
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
                self.do_open(target=init_page)  # 每次执行用例前，先初始化到首页
                print(f'正在执行的用例为:【{item3}】')
                case_results_dict['name'] = item3  # 用例名称
                elements = read_yaml2(self.element_file)
                if many:
                    col = many['case_module']
                else:
                    col = item
                element = query_case(elements, col=col)
                # 如果该用例对其他页面元素产生依赖，处理如下
                case_ = item2.get(item3)  #
                case_process_list = []  # 用例处理流程
                case_results_dict['执行步骤'] = str(case_)
                for step in case_:  # 循环遍历用例执行步骤
                    step = self.deal_parameters_depend(element_dic=step, default_element_dic=element)
                    command, target, value = packing_parameters2(step)
                    func = self.command_map.get(command)
                    case_results_dict['执行命令'] = command  # 用例执行命令
                    case_results_dict['操作元素'] = target  # 操作元素
                    case_results_dict['输入值'] = value  # 输入值
                    flag = True
                    try:
                        func(self, target, value)  # 执行函数
                    except Exception as e:
                        print(e)
                        error_info = traceback.format_exc()
                        case_results_dict['报错信息'] = str(error_info)
                        case_results_dict['运行结果'] = '失败'
                        flag = False
                    else:
                        case_results_dict['运行结果'] = '成功'
                        case_results_dict['报错信息'] = '无'
                        verify_res, keyword = self.keyword_verify(step)  # 接收检验结果
                        case_results_dict['校验关键字'] = keyword
                        case_results_dict['校验结果'] = (lambda x: '成功' if x == 'True' else '失败')(verify_res)

                    case_process_list.append(json.dumps(case_results_dict, ensure_ascii=False))
                    time.sleep(0.5)  # 每个用例执行完毕后，等待3s
                    if not flag:  # 报错了， 退出这个流程
                        break
                        # continue
                case_results_list.append(case_process_list)  # 添加运行结果到列表里
                if many:  # 执行单条用例
                    return case_results_list
        return case_results_list

    def keyword_verify(self, step):
        """关键字校验函数"""
        try:
            item = step['keyword_verify']
        except Exception as e:
            print(e)
            return 'True', 'None'
        else:
            if str(item) not in self.driver.page_source:
                print('校验失败')
                return 'False', str(item)
            else:
                return 'True', str(item)

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
        self.driver.quit()
        report_email(items, report)


if __name__ == "__main__":
    case = Case(case_file='usecase/yaml_case.yaml', element_file='elements/baidu_elements.yaml')
    case.run(report=False, many={'case_module': '登录_2', 'case_name': '密码登录3'})  # 单条执行
    # case.run(many={}, report=False)  # 全部执行
