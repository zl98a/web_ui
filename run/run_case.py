from test_case.baidu.web_test2 import Case
from base.config import rootPath
import os
from concurrent.futures import ThreadPoolExecutor


def run(browser):
    case = Case(browser=browser, case_file=os.path.join(rootPath, 'test_case/baidu/usecase/yaml_case.yaml'),
                element_file=os.path.join(rootPath, 'test_case/baidu/elements/baidu_elements.yaml'))
    # case.run(report=False, many={'case_module': '简书', 'case_name': '简书搜索'})  # 单条执行
    case.run(many={}, report=False)  # 全部执行


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:
        pool.map(run, [['chrome', '106.0'],
                       ['chrome', '98.0'],
                       ['MicrosoftEdge', '98.0'],
                       ['MicrosoftEdge', '106.0'],
                       ['MicrosoftEdge', '105.0'],
                       ['firefox', '96.0']])
