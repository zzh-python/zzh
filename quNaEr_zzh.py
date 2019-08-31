import requests
import re,time,json
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from homework_spider.quNaErZzh import quNaEr_selenium  #文件导入
from homework_spider.quNaErZzh.quNaEr_redis import save_to_redis as save

class quNaErWang(object):
    def __init__(self):
        self.driver = self.load_init_page()
        self.page=1

    #初始化driver
    @staticmethod
    def load_init_page():
        #载去哪网首页
        url = 'https://flight.qunar.com/'
        option = webdriver.ChromeOptions()
        option.add_experimental_option('excludeSwitches',['enable-automation'])
        driver = webdriver.Chrome(chrome_options=option)
        # driver.maximize_window()
        driver.get(url)
        try:
            startTime = time.time()  # 计算时间戳
            print('正在打开去哪---->>')
            wait = WebDriverWait(driver, 10)
            # 直到加载到了首页
            wait.until(EC.presence_of_element_located((By.ID, 'js_topicLink')))
        except:
            endTime = time.time()
            print('打开失败，费时---->>', endTime - startTime)
        return driver

    #传入查询目标
    def start_function(self, city_start, city_arrive, what_time=None):
        if not self.operate_city_date(city_start, city_arrive, what_time):
            return None
        # return self.get_flight_data()
        self.get_flight_data()
    #获取航班信息
    def get_flight_data(self):
        #点击直飞
        if self.page == 1:
            self.click_direct_flight_checkbox()

        #航空公司
        airline_xpath='//div[@class="air"]/span'
        flight_company_list = self.get_text_ele_list(airline_xpath)
        #起飞时间
        data_reactid_xpath='//div[@class="sep-lf"]/h2'
        data_reactid_list = self.get_text_ele_list(data_reactid_xpath)
        #到达时间
        data_arrive_xpath='//div[@class="sep-rt"]/h2'
        data_arrive_list = self.get_text_ele_list(data_arrive_xpath)
        #起飞机场  #到达机场
        airport_xpath= '//p[@class="airport"]/span[1]'
        airport_list = self.get_text_ele_list(airport_xpath)
        #价格
        price_list = self.get_price_list()
        print(price_list)
        #保存
        num=0
        for i in range(len(price_list)):
            message= "航空公司:"+ flight_company_list[i].text + "起飞时间:"+data_reactid_list[i].text + "到达时间:"+  data_arrive_list[i].text + "起飞机场："+ airport_list[num].text+ "到达机场："+ airport_list[num+1].text +"票价:"+  price_list[i]
            # print(message)
            num=num+2
            self.save_redis(message)
        #翻页
        flag=self.next_page()
        if flag == True :
            return self.get_flight_data()
        elif flag == False :
            return True



    #获取机票价格,css混淆
    def get_price_list(self):
        price_list = list()
        # 网页源码
        html_source = self.driver.page_source
        # 价格xpath 外部选取
        em_rel_list = re.findall(r'<em class="rel"><b .*?</b></em>',html_source)
        #邻近推荐
        air_tip_xpath='//div[@class="air g-tips"]/span'
        air_tip_list= self.get_text_ele_list(air_tip_xpath)
        if_pass = True
        for i in em_rel_list:
            i_list=re.findall(r'">(\d)</i>',i)
            b_list=re.findall(r'">(\d)</b>',i)
            pos_list=re.findall(r'left:-(\d\d)px',i)
            #删除邻近推荐的价格
            if air_tip_list!= None and if_pass:
                if_pass= False
                continue
            for m,n in enumerate(pos_list):
                if m == 0 : continue  #舍弃第一个值
                if len(i_list) == 3 :
                    if n == '48':
                        i_list[0] =b_list[m-1]
                    elif n == '32':
                        i_list[1] = b_list[m-1]
                    elif n == '16':
                        i_list[2] = b_list[m-1]
                elif len(i_list) == 4 :
                    if n == '64':
                        i_list[0] = b_list[m - 1]
                    elif n == '48':
                        i_list[1] =b_list[m-1]
                    elif n == '32':
                        i_list[2] = b_list[m-1]
                    elif n == '16':
                        i_list[3] = b_list[m-1]
            price=""
            for i in i_list:
                price=price + i
            price_list.append(price)
        return price_list

    #填充数据
    def operate_city_date(self, city_start, city_arrive, what_time):
        #填入城市
        fromcity_xpath = '//*[@id="dfsForm"]/div[2]/div[1]/div/input'
        if not self.send_word(city_start, fromcity_xpath):
            return False
        tocity_xpath = '//*[@id="dfsForm"]/div[2]/div[2]/div/input'
        if not self.send_word(city_arrive, tocity_xpath):
            return False
        #填入日期
        if not self.sends_date(what_time):
            return False
        #处理日期弹窗
        if self.is_date_frame:
            if not self.click_date_btn():
                return False
        #点击搜索
        if not self.click_flight_search_btn():
            return False
        return True

    #键入值
    def send_word(self, word, xpath):
        time.sleep(1)
        element = quNaEr_selenium.get_include_hide_element_for_wait(
            self.driver,
            By.XPATH,
            xpath)
        if not element:
            return False
        try:
            element.clear()
            element.send_keys(word)
        except Exception as error:
            print('element:', error)
            return False
        return True
    #输入时间
    def sends_date(self, fromdate):
        time.sleep(1)
        fromto_date_xpath = '//div[@id="js_flighttype_tab_domestic"]/form/\
            div[3]/div[1]/div/input'
        element = quNaEr_selenium.get_include_hide_element_for_wait(
            self.driver,
            By.XPATH,
            fromto_date_xpath
        )
        if not element:
            return False
        try:
            element.click()
            #删除默认日期
            for i in range(10):
                time.sleep(0.2)
                element.send_keys(Keys.BACK_SPACE)
            element.send_keys(fromdate)
        except Exception as error:
            print('sends_date_error:', error)
            return False
        return True

    #判断日期弹窗
    def is_date_frame(self):
        date_frame_xpath = '//div[@class="t"]'
        element = self.get_text_ele_list(date_frame_xpath, timeout=2)
        if not element:
            return False
        if len(element) > 0:
            return True
        return False

    def get_text_ele_list(self, texts_xpath, timeout=3):
        element = quNaEr_selenium.get_include_hide_elements_for_wait(
            self.driver,
            By.XPATH,
            texts_xpath,
            timeout=timeout
        )
        if not element:
            return None
        return element

    #点击日历弹框按钮
    def click_date_btn(self):
        time.sleep(1)
        date_btn_xpath ='//*[@id="dfsForm"]/div[3]/div[1]/div/div[1]/div[3]/b'
        element = quNaEr_selenium.get_include_hide_element_for_wait(
            self.driver,
            By.XPATH,
            date_btn_xpath
        )
        if not element:
            return False
        try:
            element.click()
        except Exception as error:
            print('click_date_btn_error:', error)
            return False
        return True
    #点击搜索
    def click_flight_search_btn(self):
        if self.is_date_frame():
            if not self.click_date_btn():
                return False
        btn_xpath = '//div[@id="js_flighttype_tab_domestic"]/form/div[4]/button'
        element = quNaEr_selenium.get_include_hide_element_for_wait(
            self.driver,
            By.XPATH,
            btn_xpath)
        if not element:
            return False
        if not quNaEr_selenium.request_num(element):
            return False
        return True

    #勾选直飞
    def click_direct_flight_checkbox(self):
        checkbox_xpath = '//label[@class="lab"]/input'
        checkbox_ele = quNaEr_selenium.get_include_hide_element_for_wait(
            self.driver,
            By.XPATH,
            checkbox_xpath,
        )
        if not checkbox_ele:
            return False
        if not quNaEr_selenium.request_num(checkbox_ele):
            return False
        return True

    def wait_until(self):
        wait = WebDriverWait(self.driver, 10)
        # 直到加载到了首页
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'air')))

    #翻页
    def next_page(self):
        #页面列表
        page_list_xpath= '//div[@class="container"]/a'
        page_list = self.get_text_ele_list(page_list_xpath)
        for index,object in enumerate(page_list,1):
            if object.text == '下一页':
                self.page =self.page + 1  #确保不点第二次直飞
                next_page_xpath=f'//div[@class="container"]/a[{index}]'
                next_page_ele = quNaEr_selenium.get_include_hide_element_for_wait(
                    self.driver,
                    By.XPATH,
                    next_page_xpath
                )
                if not next_page_ele:
                    return False
                for i in range(5):
                    #点击
                    if not quNaEr_selenium.request_num(next_page_ele):
                         self.wait_until()
                         #下拉
                         # quNaEr_selenium.move_down(self.driver)
                         time.sleep(2)
                    else:
                        return True
        return False

    #保存
    def save_redis(self,mess):
        return  save(mess)



if __name__ == '__main__':
   run=quNaErWang()
   start_city = u'广州'
   arrive_city = u'北京'
   outset_date = time.strftime(
       "%Y-%m-%d",
       time.localtime(time.time() + (3600 * 24 * 7)))

   run.start_function(start_city, arrive_city, outset_date)

