import time

from selenium import webdriver
import warnings
caps = {
    'platform': 'ANY',
    'browserName': 'chrome',
    'version': '',
}
dr = webdriver.Remote('http://192.168.169.134:5001/wd/hub', desired_capabilities=caps)
dr.get('https://www.baidu.com')
print(dr.title)
# time.sleep(10)
dr.quit()