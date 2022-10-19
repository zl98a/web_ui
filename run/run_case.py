from test_case.baidu.web_test2 import Case
from base.config import rootPath
import os

case = Case(case_file=os.path.join(rootPath, 'test_case/baidu/usecase/yaml_case.yaml'), element_file=os.path.join(rootPath, 'test_case/baidu/elements/baidu_elements.yaml'))
case.run(report=False, many={'case_module': '简书', 'case_name': '简书搜索'})  # 单条执行
# case.run(many={}, report=False)  # 全部执行
