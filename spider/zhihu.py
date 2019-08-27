'''
reference: https://juejin.im/post/5c77b673e51d4554ff57fc05
'''
import threading
import base64
import hashlib
import os
import hmac
import json
import re
import time
from http import cookiejar
from urllib.parse import urlencode
import execjs
import requests
import traceback
from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains

from driver import BaseOperat
from autogui import *
from logger import log_debug
from utils import *
from config import *


cookiespath = os.path.join(cookiesdir, 'zhihucookies.txt')
captchapath = os.path.join(captchadir, 'zhihucaptcha.jpg')

class ZhiHuConf():
    def __init__(self):
        cfs = read_config(os.path.join(CURRENTPATH, 'config', 'zhihu.json'))
        self.username = cfs['USERNAME']
        self.password = cfs['PASSWORD']
        self.login_url = cfs['LOGIN_URL']
        self.write_url = cfs['WRITE_URL']


class Account(object):

    def __init__(self, gui):
        self.conf = ZhiHuConf()
        self.username = self.conf.username
        self.password = self.conf.password
        self.gui = gui

        self.login_data = {
            'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
            'grant_type': 'password',
            'source': 'com.zhihu.web',
            'username': '',
            'password': '',
            'lang': 'en',
            'ref_source': 'other_%s'%self.conf.login_url,
            'utm_source': ''
        }
        self.session = requests.session()
        self.session.headers = {
            'accept-encoding': 'gzip, deflate, br',
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
        self.session.cookies = cookiejar.LWPCookieJar(filename=cookiespath)

    def login(self, captcha_lang: str = 'en', load_cookies: bool = True):
        """
        login zhihu
        :param captcha_lang: Captcha type: 'en' or 'cn'
        :param load_cookies: Whether to read the last saved Cookies
        :return: bool
        若在 PyCharm 下使用中文验证出现无法点击的问题，
        需要在 Settings / Tools / Python Scientific / Show Plots in Toolwindow，取消勾选
         """
        if load_cookies and self.load_cookies():
            print(' 读取 Cookies 文件')
            if self.check_login():
                print(' 登录成功')
                return True
            print('Cookies 已过期')

        self._check_user_pass()
        self.login_data.update({
            'username': self.username,
            'password': self.password,
            'lang': captcha_lang
        })

        timestamp = int(time.time() * 1000)
        self.login_data.update({
            'captcha': self._get_captcha(self.login_data['lang']),
            'timestamp': timestamp,
            'signature': self._get_signature(timestamp)
        })

        headers = self.session.headers.copy()
        headers.update({
            'content-type': 'application/x-www-form-urlencoded',
            'x-zse-83': '3_1.1',
            'x-xsrftoken': self._get_xsrf()
        })
        data = self._encrypt(self.login_data)
        login_api = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        resp = self.session.post(login_api, data=data, headers=headers)
        if 'error' in resp.text:
            print(json.loads(resp.text)['error'])
        if self.check_login():
            print(' 登录成功')
            return True
        print(' 登录失败')
        return False

    def load_cookies(self):
        """
        Read cookies file to load into the Session.
        :return: bool
        """
        try:
            self.session.cookies.load(ignore_discard=True)
            return True
        except FileNotFoundError:
            return False

    def check_login(self):
        """
        Check login status
        :return: bool
        """
        login_url = 'https://www.zhihu.com/signup'
        resp = self.session.get(login_url, allow_redirects=False)
        if resp.status_code == 302:
            self.session.cookies.save()
            return True
        return False

    def _get_xsrf(self):
        """
        get xsrf from login page
        :return: str
        """
        self.session.get('https://www.zhihu.com/', allow_redirects=False)
        for c in self.session.cookies:
            if c.name == '_xsrf':
                return c.value
        raise AssertionError(' 获取 xsrf 失败')

    def _get_captcha(self, lang: str):
        """
        request captcha API.
        :param lang: return the language of the captcha code (en/cn)
        :return: coaptcha code post parameter
         """
        if lang == 'cn':
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
        else:
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        resp = self.session.get(api)
        show_captcha = re.search(r'true', resp.text)

        if show_captcha:
            put_resp = self.session.put(api)
            json_data = json.loads(put_resp.text)
            img_base64 = json_data['img_base64'].replace(r'\n', '')
            with open(captchapath, 'wb') as f:
                f.write(base64.b64decode(img_base64))

            if lang == 'cn':
                img = Image.open(captchapath)
                import matplotlib.pyplot as plt
                plt.imshow(img)
                print(' 点击所有倒立的汉字，在命令行中按回车提交')
                points = plt.ginput(7)
                capt = json.dumps({'img_size': [200, 44],
                                   'input_points': [[i[0] / 2, i[1] / 2] for i in points]})
            else:
                self.gui.popup(captchapath)
                capt = self.gui.w.value  # 用户填写的验证码
                if not capt:
                    self.gui.l.config(text='必须填写验证码')
                    return
                # img_thread = threading.Thread(target=img.show, daemon=True)
                # img_thread.start()
                # capt = input('请输入图片里的验证码：')
            # Here you must need post catptcah code interface
            self.session.post(api, data={'input_text': capt})
            return capt
        return ''

    def _get_signature(self, timestamp: int or str):
        """
        Hmac algorithm calculates signature.
        Actually, a few fixed strings plus timestamp
        :param timestamp:
        :return: signature
         """
        # Key is fixed.
        ha = hmac.new(key=b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = self.login_data['grant_type']
        client_id = self.login_data['client_id']
        source = self.login_data['source']
        ha.update(bytes((grant_type + client_id + source + str(timestamp)), 'utf-8'))
        return ha.hexdigest()

    def _check_user_pass(self):
        """
        Check username and password
        """
        if not self.username:
            self.username = input(' 请输入手机号：')
        if self.username.isdigit() and '+86' not in self.username:
            self.username = '+86' + self.username

        if not self.password:
            self.password = input(' 请输入密码：')

    @staticmethod
    def _encrypt(form_data: dict):
        with open(os.path.join(jsdir, 'zhihuencrypt.js')) as f:
            js = execjs.compile(f.read())
            return js.call('Q', urlencode(form_data))

class PublishArticle(BaseOperat):
    def __init__(self):
        super(PublishArticle, self).__init__()
        self.conf = ZhiHuConf()
        self.initcookies()

    def initcookies(self):
        ''' cookiejar to selenium driver'''
        self.get(BASE_URL)
        cookies = cookiejar.LWPCookieJar(filename=cookiespath)
        cookies.load(ignore_discard=True)
        if os.path.exists(cookiespath):
            for cookie in cookies:
                cookie_dict = {'name': cookie.name, 'value': cookie.value}
                if cookie.expires:
                    cookie_dict['expiry'] = cookie.expires
                if cookie.path_specified:
                    cookie_dict['path'] = cookie.path
                if cookie.domain:
                    cookie_dict['domain'] =cookie.domain
                if cookie.secure:
                    cookie_dict['secure'] = cookie.secure
                self.driver.add_cookie(cookie_dict)



    def publish(self, title, topics, column='', filepath = ''):
        '''
        :param topics: the article belongs to the topic
        :param column: the article belongs to the column
        :return:
        '''
        self.get(self.conf.write_url)
        title_xp = "//*[contains(@class, 'WriteIndex-titleInput')]/textarea"
        content_xp = "//*[contains(@class, 'public-DraftEditor-content')]"
        publish_button_xp = "//*[contains(@class, 'PublishPanel-triggerButton')]"

        # 1.Fill in the body title
        self.input_data_by_xpath(title_xp,title)
        # 2.Fill in the body content
        # self.input_data_by_xpath(content_xp,content)
        # get html content
        self.use_onlinemd(filepath)
        # Let input box get the focus
        # self.driver.find_element_by_xpath(content_xp).clear()
        self.click_element_with_chains(content_xp)
        # paste content
        paste()

        imgnum = self.get_imgnum(filepath)
        if imgnum:
            time.sleep(imgnum * IMGTIME)
        else:
            time.sleep(2)

        # 3.Click to publish
        self.click_element_with_chains(publish_button_xp)

        for topic in topics:
            # 4.Choose topic
            self.input_data_by_xpath("//*[contains(@class, 'Input preventCloseOnTarget')]",topic.strip(), 1)
            try:
                self.click_element_with_chains("//*[contains(@class, 'PublishPanel-row PublishPanel-normalRow preventCloseOnTarget')]", 1)
            except:
                log_debug(traceback.format_exc())
                log_debug('%s 点击失败'%topic)


        # 5.Click "下一步"
        self.click_element_with_chains("//*[contains(@class, 'PublishPanel-button')]", 1)
        # 6.Choose whether the article is posted to the column or published directly
        if column:
            columns = self.driver.find_elements_by_xpath("//*[contains(@class, 'PublishPanel-label')]")
            for c in columns:
                if column.strip() == c.text.strip():
                    ActionChains(self.driver).move_to_element(c).click(c).perform()
        # 7.Click "确定"
        self.click_element_with_chains("//*[contains(@class, 'PublishPanel-stepTwoButton')]",2)
        current_url = self.driver.current_url
        if 'writer' not in current_url:
            print('发布成功，文章链接为：%s'%current_url)

def run(filepaths, gui=None):
    account = Account(gui)
    account.login(captcha_lang='en', load_cookies=True)
    pa = PublishArticle()
    for filepath in filepaths:
        title = get_md_title(filepath)
        tags = get_md_tags(filepath)
        if title:
            pa.publish(title=title, topics=tags, filepath=filepath)
            return 200
        else:
            return 301

