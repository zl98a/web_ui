import time
import warnings
# sys.path.append(r'C:\pythonPro\multitasking')
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.edge.options import Options  # => 引入Chrome的配置
from selenium.webdriver.chrome.options import Options  # => 引入Chrome的配置
from selenium.webdriver import ChromeOptions


def get_driver(base_url=None, browser=None):
    """获取driver对象"""
    warnings.simplefilter('ignore', ResourceWarning)
    caps = {
        'platform': 'ANY',
        'browserName': f'{browser[0]}',
        'version': f'{browser[1]}',
    }
    driver = webdriver.Remote('http://192.168.9.56:4444/wd/hub', desired_capabilities=caps)
    if base_url:
        driver.get(base_url)  # 打开初始页
    driver.maximize_window()
    return driver


class BasePage:
    # 构造函数
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 9, 0.5)  # 全局显示等待5s，

    # 元素定位操作封装
    def locator(self, loc):
        loc_ele = str(loc).split('=', 1)
        return self.wait.until(lambda driver: self.driver.find_elements(*loc_ele))

    # 输入txt为要输入的内容，loc为元素
    def input(self, loc, txt, t=0.65):
        self.locator(loc)[0].send_keys(txt)

    def open(self, url):
        self.driver.get(url)

    # 打印源码
    def page_source(self):
        return self.driver.page_source

    # 点击 loc为元素
    def click(self, loc, t=0.66):
        self.locator(loc)[0].click()

    # 清除输入框
    def clear(self, loc):
        self.locator(loc)[0].clear()

    # # 等待 需要 import time
    # def wait(self, time_):
    #     sleep(time_)

    # 关闭应用  驱动退出 大退
    def quit_(self):
        self.driver.quit()

    # 关闭应用 小退
    def close_(self):
        self.driver.close()

    # back次数设置
    def by_back(self, num=1):
        for i in range(0, num):
            self.driver.back()
            time.sleep(0.65)

    # 屏幕直到某个元素出现----应用场景在web项目
    def swipe_down(self, ele_xpath, error=True):
        swipe_x = 0
        for b in range(100):
            try:
                ele = self.locator(ele_xpath)[0]
            except Exception as e:
                print(e)
                self.driver.execute_script(f'window.scrollTo({swipe_x},{swipe_x + 300})')  # 下滑
                swipe_x += 300
                if b == 16:
                    if error:
                        assert False
                    else:
                        print('没有找到该元素~')
                        return
            else:
                return ele

    # 清除输入框
    def clear_input(self, ele, phone=''):
        self.driver.execute_script("arguments[0].value = '';", ele)
        ele.send_keys(Keys.CONTROL, 'a')
        ele.send_keys(phone)

    # 跳转句柄
    def jump_handles(self, index=-1):
        self.driver.switch_to.window(self.driver.window_handles[index])

    def execute_javascript(self, ele):
        """执行script点击"""
        self.driver.execute_script('$(arguments[0]).click()', ele)

    def pub_swipe_down(self, elm_loc=None, error=True):
        """下滑直至查找到某个元素"""
        if not elm_loc:
            print('swipe ele is not null!')
            assert False
        swipe_x = 0
        for b in range(100):
            try:
                ele = elm_loc.split('=', 1)
                find_ele = self.driver.find_element(*ele)
            except Exception as e:
                print(e)
                self.driver.execute_script(f'window.scrollTo({swipe_x},{swipe_x + 300})')  # 下滑
                swipe_x += 300
                time.sleep(1)
                if b == 20:  # 查找20次
                    if error:
                        assert False
                    else:
                        print('没有找到该元素~')
                        return
            else:
                print('找到元素了。')
                return find_ele
