# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

from abc import ABCMeta, abstractmethod
import functools
import traceback
import time
import re

from logger import *
from autogui import *
from utils import *
from config import *


def run_time(func):
    '''
    running time
    :param func:
    :return:
    '''
    @functools.wraps(func)
    def print_time(*args, **kwargs):
        func_name = func.__name__
        t0 = time.time()
        func(*args, **kwargs)
        t1 = time.time()
        log_time('[%s] is run, run time is (%s)'%(func_name, t1-t0))
    return print_time

class Driver(object):
    _instance = None
    driver = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Driver, cls).__new__(cls, *args, **kwargs)
            cls.driver = cls._instance.initdriver()
        return cls._instance

    def initdriver(self, plug=False, brower='Chrome'):
        appdata = os.getenv("APPDATA")
        if brower == 'Chrome':
            option = webdriver.ChromeOptions()
            # set browser to developer mode
            # option.add_experimental_option('excludeSwitches', ['enable-automation'])
            # set browser to not trace mode
            # option.add_argument("--incognito")
            # Remove warnings from browser that 'Chrome is under the control of automated software'
            option.add_argument('disable-infobars')
            # No interface
            # option.add_argument('headless')
            driver = webdriver.Chrome(executable_path=CHROMEDIRVER, chrome_options=option)
            driver.set_window_size(1200, 900)
        elif brower == 'FireFox':
            if plug:
                #  open %APPDATA%\Mozilla\Firefox\Profiles\ find firefox plugin，then load plugin configuration.
                firefox_plug_dir = ''
                profile_directory = os.path.join(appdata, 'Mozilla\Firefox\Profiles', firefox_plug_dir)
                profile = webdriver.FirefoxProfile(profile_directory)
            # Launch browser
            driver = webdriver.Firefox(firefox_profile=profile)
        return driver



class BaseOperat():
    ''' Base Operat Class'''

    __metaclass__ = ABCMeta

    def __init__(self):
        self.driver = Driver().driver

    @abstractmethod
    def run(self):
        '''  must be rewritten '''
        pass

    @run_time
    def waitid(self, id):
        try:
            WebDriverWait(self.driver, WAITTIME, 1).until(
                lambda x: x.find_element_by_id(id)
            )
        except:
            traceback.print_exc()
            return 0, 'wait id 20s timeout, try again'
        return 1, 'wait id finish'

    @run_time
    def waitcss(self, css):
        try:
            WebDriverWait(self.driver, WAITTIME, 1).until(
                lambda x: x.find_element_by_css_selector(css)
            )
        except:
            traceback.print_exc()
            return 0, 'wait css 20s timeout, try again'
        return 1, 'wait css finish'


    @run_time
    def waitxpath(self, xpath):
        try:
            WebDriverWait(self.driver, WAITTIME, 1).until(
                lambda x: x.find_element_by_xpath(xpath)
            )
        except:
            traceback.print_exc()
            return ERROR, 'waif xpath 20s timeout, try again'
        return SUCCESS, 'wait xpath finish'

    def get(self,url):
        self.driver.get(url)

    def elementexist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
            return True
        except:
            return False

    @run_time
    def login(self, loginurl, buttonxpath,uname_pwd_xpaths={}, sleeptime=5):
        '''
        auto login
        :param xpath: need wait this xpath element load.
        :param uname_pwd_xpaths: dict of username, password and xpaths, like:
        {'username':'xpath about username input',
        'password':'xpath about password input'}
        '''
        if not len(uname_pwd_xpaths):
            print('Login xpaths is empty!')
            exit()
        self.driver.delete_all_cookies()
        self.get(loginurl)
        self.waitxpath(buttonxpath)
        for k,v in uname_pwd_xpaths.items():
            input = self.driver.find_element_by_xpath(v)
            input.clear()
            input.send_keys(k)
        self.click_element(buttonxpath)
        time.sleep(sleeptime)
        log_action('login finish!')

    @run_time
    def input_data_by_xpath(self, xpath, content, sleeptime=0):
        ''' send content to input element '''
        self.waitxpath(xpath)
        input = self.driver.find_element_by_xpath(xpath)
        input.clear()
        input.send_keys(content)
        if sleeptime:
            time.sleep(sleeptime)


    def input_data_by_name(self,name, content, sleeptime=0):
        input = self.driver.find_element_by_name(name)
        input.clear()
        input.send_keys(content)
        if sleeptime:
            time.sleep(sleeptime)



    @run_time
    def choice_select(self, xpath, content, sleeptime=0):
        '''
        Choick select element
        :param xpath: select xpath
        :param content: select value
        '''
        self.waitxpath(xpath)
        select = Select(self.driver.find_element_by_xpath(xpath))
        #  select the value of text='xxx'
        select.select_by_visible_text(content)
        if sleeptime:
            time.sleep(sleeptime)

    def click_element(self, xpath, sleeptime=0):
        self.waitxpath(xpath)
        element = self.driver.find_element_by_xpath(xpath)
        element.click()
        if sleeptime:
            time.sleep(sleeptime)


    def click_element_with_chains(self, xpath, sleeptime=0):
        self.waitxpath(xpath)
        element = self.driver.find_element_by_xpath(xpath)
        ActionChains(self.driver).move_to_element(element).click(element).perform()
        if sleeptime:
            time.sleep(sleeptime)

    def get_data(self, xpath, attribute='',sleeptime=0):
        ''' get element data '''
        self.waitxpath(xpath)
        element = self.driver.find_element_by_xpath(xpath)
        if attribute:
            res = element.get_attribute(attribute)
        else:
            res = element.text
        if sleeptime:
            time.sleep(sleeptime)
        return res

    @run_time
    def quit(self):
        '''quit driver'''
        self.driver.quit()


    def get_imgnum(self, filepath):
        '''
        Get the number of images in the article,
        pause the time when copying and pasting content.
        '''
        txt = get_md_content(filepath)
        imgs = re.findall(r'!\[\]\(http:.*?\)', txt)
        imgs.extend(re.findall(r'!\[\]\(https:..*?\)', txt))
        return len(imgs)

    def use_onlinemd(self, filepath):
        '''
        Convert markdown to html.
        When the article publishes the platform (like zhihu), the style will not be confused.
        '''
        mdstr = get_md_content(filepath)

        js = 'window.open("%s");' % BASE_URL
        self.driver.execute_script(js)
        handles = self.driver.window_handles  # Get the current window handle
        for handle in handles:  # Switch window
            if handle != self.driver.current_window_handle:
                self.driver.switch_to.window(handle)
                break

        fileurl = 'file://%s%s'%(CURRENTPATH, '/onlinemd/index.html')
        self.get(fileurl)
        self.click_element_with_chains('//*[@id="input"]')
        # Copy and paste the content
        copypaste(mdstr)
        # click preview
        self.click_element('/html/body/button[2]')
        self.click_element_with_chains('//*[@id="outputCtt"]')
        # Click to copy (will select all content)
        self.click_element('/html/body/button[1]')
        time.sleep(1)
        # Copy to clipboard
        copy()
        time.sleep(0.5)
        self.driver.close()
        self.driver.switch_to.window(handles[0])