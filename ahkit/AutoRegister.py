#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import getpass
import os
import sys
import time

from Crypto.Cipher import AES
from selenium import webdriver
import toml
import yaml


class AutoRegisterConfig:
    def __init__(self):
        setting_dir = os.path.join(os.environ['HOME'], '.config', 'ahkit')
        is_dir = os.path.isdir(setting_dir)
        if not is_dir:
            os.makedirs(setting_dir)

        self.setting_path = os.path.join(setting_dir, 'settings.toml')

    def status(self):
        '''Check the Configuration Status'''

        return os.path.isfile(self.setting_path)

    def load(self):
        '''Load a Configuration File'''

        f = open(self.setting_path, 'r')
        setting_data = toml.loads(f.read())
        f.close()
        cipher = AES.new(base64.b64encode(setting_data['id']) + 'X' * (16 - len(base64.b64encode(setting_data['id']))))

        self.uid = setting_data['id']
        self.pw = cipher.decrypt(base64.b64decode(setting_data['pass'])).replace('X', '')
        self.name = setting_data['name']
        self.browser = setting_data['browser']

    def save(self):
        '''Save a Configuration File'''

        print '*** Save a Configuration File ***'

        s_id = raw_input('Input Student ID: ')
        cipher = AES.new(base64.b64encode(s_id) + 'X' * (16 - len(base64.b64encode(s_id))))
        s_pass = getpass.getpass('Input Password: ')
        s_pass_confirm = getpass.getpass('Input Confirm Password: ')
        if s_pass != s_pass_confirm:
            print "Error: Password don't match."
            sys.exit(0)
        s_pass = base64.b64encode(cipher.encrypt(s_pass + 'X' * (16 - len(s_pass))))
        s_name = raw_input('Input Name or Nickname: ')
        s_browser = raw_input('Input Browser (Firefox: 0, Google Chome: 1): ')
        s_browser = s_browser if s_browser == '1' else '0'

        settings = '''################
# Setting File #
################

# Student ID
id = "%s"

# Password
pass = "%s"

# Your name or nickname
name = "%s"

# Firefox: 0, Google Chrome: 1
browser = "%s"
''' % (s_id, s_pass, s_name, s_browser)
        with open(self.setting_path, 'w') as f:
            f.write(settings)

        print 'Save a Configuration File to ' + self.setting_path + '\n'

        self.load()


class AutoRegister:
    def __init__(self, config, files):
        self.__id = config.uid
        self.__pass = config.pw
        self.__browser = config.browser
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
        if self.__browser == '0':
            browser = webdriver.Firefox()
        else:
            browser = webdriver.Chrome()

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

        # 活動記録機能
        browser.find_element_by_xpath("//a[@class='menubutton' and text()='活動記録機能']").click()

        for data in self.__parse_yaml():
            activity_histories = browser.find_elements_by_xpath("//td[@align='left']/a[@class='blue']")
            ah_date = {ah.text.encode('utf-8').split()[0].replace('/', ''): ah for ah in activity_histories}
            yyyymmdd = data['syear'] + data['smonth'] + data['sday']
            if yyyymmdd in ah_date.keys():
                # 修正
                stage = 'modify'
                ah_date[yyyymmdd].click()
                browser.find_element_by_xpath("//input[@value='　変　更　']").click()

            else:
                # 新規登録
                stage = 'new'
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
            if stage == 'modify':
                browser.find_element_by_xpath("//a[@class='return']").click()
            time.sleep(1)
