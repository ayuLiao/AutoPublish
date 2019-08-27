import os
import json

REALPATH = os.path.realpath(__file__)
CURRENTPATH = os.path.dirname(REALPATH)
# js which spider need used
jsdir = os.path.join(CURRENTPATH, 'js')
# when login success, save the cookies
cookiesdir = os.path.join(CURRENTPATH, 'cookies')
if not os.path.exists(cookiesdir):
    os.makedirs(cookiesdir)
# website captcha
captchadir = os.path.join(CURRENTPATH, 'captcha')
if not os.path.exists(captchadir):
    os.makedirs(captchadir)

SUCCESS = 1
FAIL = 0
ERROR = -1

# Page element wait time.
WAITTIME = 20
# Image upload wait time.
IMGTIME = 3

LOGER_PATH = os.path.join(CURRENTPATH, 'logs')
# 修改成chromedirver在你本地的位置
CHROMEDIRVER = os.path.join(CURRENTPATH, 'res','chromedriver_68')

# Open some page to load cookies.
BASE_URL = 'https://baidu.com'

def read_config(path):
    with open(path, 'r') as f:
        res = f.read()
    return json.loads(res)

