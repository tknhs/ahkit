#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from selenium import webdriver
import yaml


class AutoRegister:
    def __init__(self, uid, pw, files):
        self.__id = uid
        self.__pass = pw
        self.__files = files

    def __parse_yaml(self):
        for f in self.__files:
            date_dict = {}
            date_list = f.split('.')[0].split('_')
            start = date_list[0]
            date_dict['syear'] = start[:4]
            date_dict['smonth'] = start[4:6]
            date_dict['sday'] = start[6:]
            end = date_list[1]
            date_dict['eyear'] = end[:4]
            date_dict['emonth'] = end[4:6]
            date_dict['eday'] = end[6:]

            yaml_file = open(f, 'r')
            data = yaml.load(yaml_file)
            for k, v in data.items():
                if type(v) == list:
                    # 重複削除 and None削除
                    items = list(set([x for x in v if x != None]))
                    data[k] = [''] if items == [] else items
                elif v == None:
                    data[k] = ''
                elif type(v) in [int, float]:
                    data[k] = str(v)
            yaml_file.close()

            data.update(date_dict)
            yield data

    def auto_register(self):
        browser = webdriver.Firefox()
        browser.get('http://portal10.mars.kanazawa-it.ac.jp/portal/student')
        assert "金沢工業大学　学生ポータルサイト" in browser.title.encode('utf-8')

        # ポータルログイン
        browser.find_element_by_xpath("//input[@name='uid']").send_keys(self.__id)
        browser.find_element_by_xpath("//input[@name='pw']").send_keys(self.__pass)
        browser.find_element_by_xpath("//input[@name='SUBMIT']").send_keys('\n')

        # 修士研究活動支援
        browser.find_element_by_xpath("//a[@target='kougaku']").click()
        browser.close()
        browser.switch_to_window("kougaku")
        assert "修士研究活動支援" in browser.title.encode('utf-8')

        for data in self.__parse_yaml():
            # 活動記録機能
            browser.find_element_by_xpath("//a[@class='menubutton' and text()='活動記録機能']").click()
            activity_histories = browser.find_elements_by_xpath("//td[@align='left']/a[@class='blue']")
            ah_date = {ah.text.encode('utf-8').split()[0].replace('/', ''): ah for ah in activity_histories}
            yyyymmdd = data['syear'] + data['smonth'] + data['sday']
            if yyyymmdd in ah_date.keys():
                # 修正
                ah_date[yyyymmdd].click()
                browser.find_element_by_xpath("//input[@value='　変　更　']").click()

            else:
                # 新規登録
                browser.find_element_by_xpath("//input[@value='活動記録の新規登録']").click()
                browser.find_element_by_xpath("//input[@name='syear']").send_keys(data['syear'])
                browser.find_element_by_xpath("//input[@name='smonth']").send_keys(data['smonth'])
                browser.find_element_by_xpath("//input[@name='sday']").send_keys(data['sday'])
                browser.find_element_by_xpath("//input[@name='eyear']").send_keys(data['eyear'])
                browser.find_element_by_xpath("//input[@name='emonth']").send_keys(data['emonth'])
                browser.find_element_by_xpath("//input[@name='eday']").send_keys(data['eday'])

            # 活動記録記入
            k_jikan = browser.find_element_by_xpath("//input[@name='k_jikan']")
            k_jikan.clear()
            k_jikan.send_keys(data['activity_time'])
            k_naiyou = browser.find_element_by_xpath("//textarea[@name='k_naiyou']")
            k_naiyou.clear()
            k_naiyou.send_keys(', '.join(data['activity_content']))
            s_jikan = browser.find_element_by_xpath("//input[@name='s_jikan']")
            s_jikan.clear()
            s_jikan.send_keys(data['guidance_time'])
            s_naiyou = browser.find_element_by_xpath("//textarea[@name='s_naiyou']")
            s_naiyou.clear()
            s_naiyou.send_keys(', '.join(data['guidance_content']))

            browser.find_element_by_xpath("//input[@value='　登　録　']").click()
            time.sleep(1)
