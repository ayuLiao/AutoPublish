import requests
import traceback
from http import cookiejar
from selenium.webdriver.common.keys import Keys

from driver import *
from utils import *
from config import *

cookiespath = os.path.join(cookiesdir, 'doubancookies.txt')

class DouBanConf():
    def __init__(self):
        cfs = read_config(os.path.join(CURRENTPATH, 'config', 'douban.json'))
        self.username = cfs['USERNAME']
        self.password = cfs['PASSWORD']
        self.login_url = cfs['LOGIN_URL']
        self.write_url = cfs['WRITE_URL']

class Account():
    def __init__(self,gui):
        self.gui = gui
        self.conf = DouBanConf()
        self.session = requests.session()
        self.session.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.session.cookies = cookiejar.LWPCookieJar(filename=cookiespath)

    def load_cookies(self):
        try:
            self.session.cookies.load(ignore_discard=True)
            return True
        except FileNotFoundError:
            return False

    def check_login(self):
        resp = self.session.get('https://www.douban.com/mine/', allow_redirects=False)
        if resp.status_code == 302:
            u = 'https://www.douban.com/people/'
            if u in resp.headers['Location']:
                return True
        return False

    def login(self,  load_cookies: bool = True):
        if load_cookies and self.load_cookies():
            print(' 读取 Cookies 文件')
            if self.check_login():
                print(' 登录成功')
                return True
            print('Cookies 已过期')

        headers = self.session.headers.copy()
        headers.update({
            'Host': 'accounts.douban.com',
            'Origin': 'https://accounts.douban.com',
            'Referer': 'https://accounts.douban.com/passport/login'
        })

        data = {
            'ck':'',
            'name': self.conf.username,
            'password': self.conf.password,
            'remember': 'true',
            'ticket': ''
        }

        req = self.session.post(self.conf.login_url, data=data, headers=headers)
        reqj = req.json()
        if reqj['status'] == 'failed':
            print('登录失败，原因：%s'%reqj['description'])
        else:
            print('登录成功')
            self.session.cookies.save()


class PublishArticle(BaseOperat):
    def __init__(self):
        super(PublishArticle, self).__init__()
        self.driver.maximize_window()
        self.conf = DouBanConf()
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

    def publish(self, title, filepath, tags=[] ):
        self.get(self.conf.write_url)
        title_xp = "//*[contains(@class, 'note-editor-input')]"
        content_xp = "//*[contains(@class, 'public-DraftEditor-content')]"
        self.input_data_by_xpath(title_xp, title)
        self.use_onlinemd(filepath)
        self.click_element_with_chains(content_xp)
        paste()
        time.sleep(2)

        imgnum = self.get_imgnum(filepath)
        if imgnum:
            time.sleep(imgnum * IMGTIME)
        else:
            time.sleep(2)

        button = "//*[contains(@class, 'note-editor-button-submit')]"
        self.click_element_with_chains(button)

        tag_xp = "//*[contains(@class, 'tag-input-fieldset')]/input"
        input_element = self.driver.find_element_by_xpath(tag_xp)
        input_element.clear()
        for tag in tags:
            input_element.send_keys(tag)
            input_element.send_keys(Keys.ENTER)

        checkbox_xp = '//*[@id="note-editor-popup-setting-terms-original"]'
        self.click_element_with_chains(checkbox_xp)
        time.sleep(3)
        self.click_element("//*[contains(@class, 'note-editor-popup-setting-submit')]/button", 2)
        current_url = self.driver.current_url
        if 'note' not in current_url:
            print('发布成功，文章链接为：%s' % current_url)

def run(filepaths, gui=None):
    account = Account(gui)
    account.login(load_cookies=True)
    pa = PublishArticle()
    for filepath in filepaths:
        title = get_md_title(filepath)
        tags = get_md_tags(filepath)
        if title:
            pa.publish(title=title, tags=tags,filepath=filepath)
            return 200
        else:
            return 301

