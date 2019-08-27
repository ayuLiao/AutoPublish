import os
import time
import requests
from http import cookiejar
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from driver import BaseOperat
from autogui import copypaste

from utils import *
from config import *

cookiespath = os.path.join(cookiesdir, 'csdncookies.txt')

class CSDNConf():
    def __init__(self):
        cfs = read_config(os.path.join(CURRENTPATH, 'config', 'csdn.json'))
        self.username = cfs['USERNAME']
        self.password = cfs['PASSWORD']
        self.login = cfs['LOGIN']
        self.login_url = cfs['LOGIN_URL']
        self.write_url = cfs['WRITE_URL']


class Account():

    def __init__(self,gui):
        self.gui = gui
        self.conf = CSDNConf()
        self.session = requests.session()
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.3',
            'content-Type': 'application/json;charset=UTF-8',
            'x-requested-with': 'XMLHttpRequest',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'connection': 'keep-alive'
            }

        self.session.cookies = cookiejar.LWPCookieJar(filename=cookiespath)

    def load_cookies(self):
        try:
            self.session.cookies.load(ignore_discard=True)
            return True
        except FileNotFoundError:
            return False

    def check_login(self):
        resp = self.session.get('https://me.csdn.net/api/user/get?username=%s'%
                                requests.utils.dict_from_cookiejar(self.session.cookies)['UserName'])
        if resp.status_code == 200:
            if resp.json()['code'] == 200:
                return True
            print('旧cookie超时，需重新登录')
            print(resp.text)
        return False


    def login(self, load_cookies: bool = True):

        if load_cookies and self.load_cookies():
            print(' 读取 Cookies 文件')
            if self.check_login():
                print(' 登录成功')
                return True
            print('Cookies 已过期')

        # get default cookies
        req = self.session.get(self.conf.login)

        url = self.conf.login_url
        data = {
            "loginType": "1",
            "pwdOrVerifyCode": self.conf.password,
            "userIdentification": self.conf.username,
            "uaToken":"",
            "webUmidToken":""
        }
        headers = self.session.headers.copy()
        headers.update({
            'referer': 'https://passport.csdn.net/login',
            'origin': 'https://passport.csdn.net',
            'Host': 'passport.csdn.net',
        })
        # csdn use request payload， so we need json.dumps json
        req = self.session.post(url, data=json.dumps(data), headers=headers)
        if req.json()['code'] == '0':
            print('登录成功')
            self.session.cookies.save()
        else:
            # Wind control judgment account
            print('code: %s, message: %s'%(req.json()['code'], req.json()['message']))

class PublishArticle(BaseOperat):
    def __init__(self):
        super(PublishArticle, self).__init__()
        self.driver.maximize_window()
        self.conf = CSDNConf()
        self.initcookies()

    def initcookies(self):
        self.get(BASE_URL)
        if os.path.exists(cookiespath):
            cookies = cookiejar.LWPCookieJar(filename=cookiespath)
            cookies.load(ignore_discard=True)
            for cookie in cookies:
                cookie_dict = {'name': cookie.name, 'value': cookie.value}
                if cookie.expires:
                    cookie_dict['expiry'] = cookie.expires
                if cookie.path_specified:
                    cookie_dict['path'] = cookie.path
                if cookie.domain:
                    cookie_dict['domain'] = cookie.domain
                if cookie.secure:
                    cookie_dict['secure'] = cookie.secure
                self.driver.add_cookie(cookie_dict)
        else:
            self.login()

    def login(self):
        self.get(self.conf.login)
        # use username and password login
        self.click_element('//*[@id="app"]/div/div/div[1]/div[2]/div[5]/ul/li[2]/a',2)
        self.input_data_by_xpath('//*[@id="all"]', self.conf.username)
        self.input_data_by_xpath('//*[@id="password-number"]', self.conf.password, 2)
        self.click_element('//*[@id="app"]/div/div/div[1]/div[2]/div[5]/div/div[6]/div/button')
        print('login success')

    def publish(self, title,filepath, tags=[], classify=[]):
        '''
        :param tags: Article label
        :param classify: Personal classification
        :return:
        '''
        self.get(self.conf.write_url)
        # Fill in title and content
        title_xp = '/html/body/div[1]/div[1]/div[1]/div/div[1]/input'
        self.driver.find_element_by_xpath(title_xp).clear()
        time.sleep(0.5)
        self.input_data_by_xpath(title_xp, title)
        self.click_element_with_chains(title_xp)
        content_xp = '/html/body/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/pre'
        # self.input_data_by_xpath(content_xp, content)

        # Let the browser focus on the content input box.
        self.driver.find_element_by_xpath(content_xp).clear()
        time.sleep(0.5)
        self.click_element_with_chains(content_xp)
        time.sleep(0.5)
        with open(filepath, 'r') as f:
            content = f.read()
        copypaste(content) # copy and paste
        imgnum = self.get_imgnum(filepath)
        if imgnum:
            time.sleep(imgnum * IMGTIME)
        else:
            time.sleep(2)

        # Click post article
        self.click_element('/html/body/div[1]/div[1]/div[1]/div/div[2]/button')

        # Fill tags
        taglist_xp = '//*[@id="tagList"]/button'
        self.waitxpath(taglist_xp)
        elements = self.driver.find_elements_by_xpath(taglist_xp)
        taglist_elem= elements[0]
        classify_elem = elements[1]
        for i, tag in enumerate(tags):
            taglist_elem.click()
            time.sleep(0.5)
            self.input_data_by_xpath('//*[@id="tagList"]/div[' + str(i + 1) + ']/span',tag)

        # Personal classification
        # for c in classify:
        #     classify_elem.click()
        #     self.input_data_by_xpath('//*[@id="tagList"]/div[' + str(i + 1) + ']/span', c)
        time.sleep(0.5)
        # CSDN的文章分类, 设个默认值
        self.csdn_article_category = '原创'
        time.sleep(0.5)
        # CSDN的博客分类, 设个默认值
        self.csdn_blog_category = '后端'
        select = Select(self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div[1]/div[4]/div[1]/div/select'))
        select.select_by_visible_text(self.csdn_article_category)
        select = Select(self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div[1]/div[4]/div[2]/div/select'))
        select.select_by_visible_text(self.csdn_blog_category)
        # 发布文章
        self.click_element('/html/body/div[1]/div[2]/div/div/div[2]/button[3]')
        print('CSDN 发布成功')


def run(filepaths, gui=None):
    account = Account(gui)
    account.login(load_cookies=True)
    pa = PublishArticle()
    for filepath in filepaths:
        title = get_md_title(filepath)
        tags = get_md_tags(filepath)
        if title:
            pa.publish(title=title, tags=tags,classify=tags, filepath=filepath)
            return 200
        else:
            return 301
