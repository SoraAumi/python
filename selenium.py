# -*- coding: utf-8 -*-
import os
import time
import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
#要打卡的人所在的行数，第一个0不好去，要加的可以在后面加
id_list=[0,100,85]
id_list=sorted(id_list)
#获得时间
date_count=datetime.datetime.now().day + 4 #时间后具体加的数字需要根据表格实际情况调试
driver = webdriver.Chrome()
driver.get("https://docs.qq.com/sheet/DQ0pHaVpUSmVTbkVN?tab=BB08J2")#将健康表的地址copy过来就行。
time.sleep(1)
driver.find_element_by_class_name('login-button').click()#点击登入按钮
time.sleep(1)
driver.find_element_by_class_name('inactive').click()#点击登入按钮
time.sleep(1)
driver.switch_to.frame(driver.find_element_by_id('login_frame'))
driver.find_element_by_class_name('img_out_focus').click()
#登入账号,用快速登入的功能,前提,已经电脑qq登入了
#driver.switch_to.parent_frame()
time.sleep(1)
driver.maximize_window()
time.sleep(1)
driver.find_element_by_xpath('//*[@id="canvasContainer"]/div[1]/div[2]').click()
time.sleep(0.5)

#移动到表头再到具体日期
driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.HOME)
driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.CONTROL, Keys.UP)
for i in range(0, date_count):#这里修改跳到信息的那一行
    driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.RIGHT)
####################################################################################
#对所有要打卡的人
for i in range(len(id_list)-1):
    for i in range(id_list[i], id_list[i+1]-1):#这里的循环的次数，修改为自己的信息所在的行号。
    #如果无效，可以将其改为(driver).key_down(Keys.ENTER).perform()
        driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
    #以下的的信息填写为自己的信息即可，你有多少列信息，就重复多少次
    driver.find_element_by_id('alloy-simple-text-editor').click()
    driver.find_element_by_id('alloy-simple-text-editor').send_keys("36."+str(random.randint(1,9)))
    driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.TAB)
    driver.find_element_by_id('alloy-simple-text-editor').click()
    driver.find_element_by_id('alloy-simple-text-editor').send_keys("36."+str(random.randint(1,9)))
    driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.ENTER)
    driver.find_element_by_id('alloy-simple-text-editor').send_keys(Keys.LEFT)
time.sleep(1)
driver.close()
os._exit()