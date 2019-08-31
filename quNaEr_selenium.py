# encoding=utf-8

import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from imp import reload
import sys
reload(sys)
# sys.setdefaultencoding('utf-8')


def get_cur_line():
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    return '%s, %s, ' % (f.f_code.co_name, str(f.f_lineno))

#判断某个元素是否被加到了dom树里，并不代表该元素一定可见
def get_element_for_wait(driver, by, by_s, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((
            by, by_s)))
        ele = driver.find_element(by, by_s)
        return ele
    except Exception:
        pass
    return ''

def get_elements_for_wait(driver, by, by_s, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((
            by, by_s)))
        ele = driver.find_elements(by, by_s)
        return ele
    except:
        pass
    return ''

#判断某个元素是否可见. 可见代表元素非隐藏，并且元素的宽和高都不等于0
def get_include_hide_element_for_wait(driver, by, by_s, timeout=15):
    try:
        ele = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, by_s))
        )
        return ele
    except:
        pass
    return ''

def get_include_hide_elements_for_wait(driver, by, by_s, timeout=15):
    try:
        ele = WebDriverWait(driver, timeout).until(
            EC.visibility_of_all_elements_located((by, by_s))
        )
        return ele
    except:
        pass
    return ''

#点击
def request_num(element, allow_num=2):
    num = 1  #请求次数
    while True:
        if num > allow_num:
            return False
        if not element:
            num += 1
            time.sleep(1)
            continue
        try:
            element.click()
        except:
            num += 1
            continue
        return True

def move_down(driver):
    # 执行js代码 下拉滚动条
    js = 'window.scrollBy(0, 8000)'
    # 执行js
    driver.execute_script(js)