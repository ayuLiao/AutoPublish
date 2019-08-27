
<p align="center"><img src="https://raw.githubusercontent.com/ayuLiao/images/master/AutoPublishicon.png"></p>
<h1 align="center">AutoPublish</h1>

&nbsp;

[![author][autopublish-author]][my-zhihu] ![docs][autopublish-docs] ![py-version][py-version]  ![license][autopublish-license]

## 简介

AutoPublish：文章多平台发布小工具，主要使用`requests`,`selenium`,`autogui`实现

AutoPublish的主要逻辑：

+ 1.通过`requests`或`selenium`进行平台登录
+ 2.使用`selenium`与`autogui`进行MarkDown文章的格式化与发布

优势：

+ 1.快速稳定，发布文章格式不会乱
+ 2.安全，账号密码不必上传到第三方

## 使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用

1.进入 config 目录，配置自己平台的账号与密码

如：想自动将文章发送到知乎，则打开 config/zhihu.json ，USERNAME 为你的账号，PASSWORD 为你的密码。

```
{
  "USERNAME":"你的账号",
  "PASSWORD":"你的密码",
  "LOGIN_URL":"https://www.zhihu.com/signin?next=%2F",
  "WRITE_URL":"https://zhuanlan.zhihu.com/write"
}
```

其他平台类似

2.修改配置

因为使用了selenium，所以你需要下载对应浏览器的中间驱动，推荐使用Chrome或Firefox(AutoPublish已经支持两者)

点击这里[ChromeDriver下载](https://chromedriver.chromium.org/downloads)

注意：ChromeDriver的版本要与Chrome版本对应(自行Google)

下载ChromeDriver后，修改 config.py 的 CHROMEDIRVER，将其修改为你本地ChromeDriver所在的路径

3.使用

```bash
python tkmain.py
```

2019年8月27效果：

<iframe src="//player.bilibili.com/player.html?aid=65553690&cid=113753898&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

4.分享给非程序员朋友使用

推荐使用pyinstaller对程序进行打包

```bash
pyinstaller -i xxx.ico -n xxx -w -D tkmain.py
```

可以参考：[Pyinstaller 使用](https://zhuanlan.zhihu.com/p/65731845)

## TODO

- [x] 知乎
- [x] CSDN
- [x] 豆瓣日志
- [ ] segmentfault
- [ ] 开源中国
- [ ] 简书
- [ ] 掘金
- [ ] 博客园

## 项目结构简介

```
├── captcha # 不同平台登录时的验证码
├── config # 不同平台的配置
├── js # 登录平台时，JS逆向代码
├── onlinemd # MarkDown文章生成样式，可以替换css修改成自己想要的样式
│   ├── css
│   ├── imgs
│   ├── js
│   ├── pageThemes
│   └── themes
├── res # ChromeDriver
├── spider # 不同平台对应的爬虫
│   ├── __init__.py
│   ├── csdn.py
│   ├── douban.py
│   └── zhihu.py 
├── config.py # 配置
├── driver.py # selenium相关
├── error.py # 错误定义
├── tkmain.py # 主入口
└── utils.py # 工具类
```

## 协助开发

个人精力有限，欢迎大家的PR。

## 个人公众号

欢迎关注个人公众号

![](https://raw.githubusercontent.com/ayuLiao/images/master/20190821150724.png)


[autopublish-author]: https://img.shields.io/badge/Author-ayuLiao-blue.svg
[my-zhihu]: https://www.zhihu.com/people/ayuliao
[autopublish-docs]: https://img.shields.io/badge/docs-doing-red.svg
[py-version]: https://img.shields.io/badge/python-3.5%2B-blue
[autopublish-license]: https://img.shields.io/badge/license-MIT-green


