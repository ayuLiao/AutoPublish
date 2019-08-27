import re
import time
import functools
import markdown

from logger import *
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


def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def read_file(path):
    with open(path, 'r') as f:
        res = f.read()
    return res


def md2html(filename):
    ''' markdown convers html '''

    mdpath = os.path.join(CURRENTPATH, 'md', filename)
    if not os.path.exists(mdpath):
        return False, 'md file not exists!'

    with open(mdpath, 'r') as f:
        mdstr = f.read()

    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
            'markdown.extensions.toc']

    html = '''
    <html lang="zh-cn">
    <head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type" />
    <link href="default.css" rel="stylesheet">
    <link href="github.css" rel="stylesheet">
    </head>
    <body>
    %s
    </body>
    </html>
    '''

    ret = markdown.markdown(mdstr, extensions=exts)
    content = html % ret
    htmlpath = os.path.join(CURRENTPATH, 'html', filename.replace('.md', '.html'))
    with open(htmlpath, 'w') as f:
        f.write(content)
    print('finish')
    return True, htmlpath

def filter_emoji(desstr, restr=''):
    ''' filter emoji in text '''
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)

def get_md_content(filepath):
    with open(filepath, 'r') as f:
        res = f.read()
    c = re.findall('---\n.*?---\n', res, re.DOTALL)
    if not c:
        return -1
    return res.replace(c[0], '')

def get_md_title(filepath):
    with open(filepath, 'r') as f:
        res = f.read()
    titles = re.findall('title:(.*?)\n', res)
    if not titles:
        return -1
    return titles[0]

def get_md_tags(filepath):
    with open(filepath, 'r') as f:
        res = f.read()
    tags = re.findall('tags:(.*?)\n', res)
    if not tags:
        return -1
    return tags





