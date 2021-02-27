# yfnews新闻站说明文档

## 文档目录

- [yfnews新闻站说明文档](#yfnews新闻站说明文档)
  - [文档目录](#文档目录)
  - [需求说明](#需求说明)
  - [技术介绍](#技术介绍)
    - [编程语言：python](#编程语言python)
    - [数据库：mongodb](#数据库mongodb)
    - [爬虫：scrapy](#爬虫scrapy)
    - [Web框架：flask](#web框架flask)
    - [html渲染引擎：Jinja2](#html渲染引擎jinja2)
    - [文本分析：Jieba中文分词库](#文本分析jieba中文分词库)
  - [数据结构](#数据结构)
    - [数据id](#数据id)
    - [tag常量表](#tag常量表)
    - [newsTable结构](#newstable结构)
    - [userTable结构](#usertable结构)
    - [historyTable结构](#historytable结构)
    - [tagIndexTable结构](#tagindextable结构)
    - [newsCacheTable结构](#newscachetable结构)
  - [运维指南](#运维指南)
    - [mongodb启动与关闭](#mongodb启动与关闭)
    - [web模块的启动与关闭](#web模块的启动与关闭)
    - [爬虫模块的启动与关闭](#爬虫模块的启动与关闭)
    - [常量表更新](#常量表更新)
    - [新增爬取网站](#新增爬取网站)
    - [修改爬虫日志输出](#修改爬虫日志输出)
    - [部署到远程服务器](#部署到远程服务器)
      - [环境安装](#环境安装)
      - [迁移数据库](#迁移数据库)
      - [修改目录配置](#修改目录配置)
      - [crontab定时调用爬虫](#crontab定时调用爬虫)
  - [http请求接口](#http请求接口)
    - [注册](#注册)
    - [登录](#登录)
    - [登出](#登出)
    - [资讯推荐](#资讯推荐)
    - [全库检索](#全库检索)
    - [查看单条新闻](#查看单条新闻)
    - [删除新闻](#删除新闻)
    - [删除标签](#删除标签)
    - [添加标签](#添加标签)
    - [修改从新闻作者、类别、股票代码](#修改从新闻作者类别股票代码)
    - [爬虫专用接口：新增文章tag转化为id，修改倒排索引表](#爬虫专用接口新增文章tag转化为id修改倒排索引表)

## 需求说明

获取网络上公开发布的新闻资讯，格式化存入数据库，以供浏览查询
为此，需要持续地进行资讯收集，对于已经收录进入数据库的数据内容，也要提供展示与修改方式。
故项目分为web与爬虫个模块，爬虫模块爬取资讯存入数据库，而web模块提供对数据库的http修改接口、前端展示界面

目前已经实现的功能如下：

1. 使用爬虫爬取新闻的文字内容
2. 自动分析文本，提取关键词
3. 简单的文章重复检测
4. 根据指定的常量表，构建倒排索引便于检索
5. 提供http接口，能够独立于浏览器完成删改查
6. 提供网页版前端，便于阅读、修改新闻，支持PC端与手机端

## 技术介绍

### 编程语言：python

使用python3编写，用pip3管理依赖

依赖库及安装如下：
爬虫-scrapy:pip3 install scrapy
python web框架-flask:pip3 install flask
web服务器-gunicorn：pip3 install gunicorn
数据库-mongoDB:sudo apt-get install mongodb
数据库操作接口-pymongo:pip3 install pymongo
分词器-jieba:pip3 install jieba
中文排序工具-pypinyin:pip3 install pypinyin
定时任务管理工具-apscheduler：pip3 install apscheduler

由于文章重复检测使用的hash函数取自内置hashlib库的shake_128()函数，需要3.6及以上版本的python(否则hashlib不支持shake_128())

### 数据库：mongodb

mongodb以C++编写，是结构松散但也功能丰富的非关系型数据库，默认端口27017
mongodb需要由多个数据库构成，每个数据库又含有多张表，表内存放数据

本项目使用yanfuNewsDB，含有五张数据表，负责存储新闻内容、用户信息、历史数据、倒排索引、增量缓存记录，具体说明见[数据结构](#数据结构)

项目基于pymongo封装了对数据库的操作，存放在目录db中：

- /yfnews
  - /newsProject
    - /flasker
      - /db

项目中用到的pymongo语句形如：

```Python
db = pymongo.MongoClient('127.0.0.1', 27017) #建立连接
news_table = db.yanfuNewsDB.newsTable #从数据库连接获取需要的表
news_table.find({'查询字段':需要的值},{'返回时需要筛选的字段':1表示需要,0标识不需要}) #查表
news_table.update_one({'查询字段':需要的值},{'$set':{'要求改的字段':修改值}}) #更改数据
news_table.insert_many({...}) #插入多条数据
```

需要注意的是，_many查询查表的返回值是一个pymongo.cursor.Cursor对象，是对查询结果的一次性遍历器，转换为list之后才能持续地访问查询结果

[回到目录](#yfnews新闻站说明文档)

### 爬虫：scrapy

scrapy是python常用的爬虫框架，可以根据需求灵活更改
scrpay的结构目录如下：

- /yfnews
  - /spider # 工程目录
    - run.sh # 爬虫运行脚本
    - scrapy.cfg # 配置文件
    - /spider
      - items.py # 设置将要爬的数据格式
      - pipelines.py # 处理格式化数据
      - settings.py # 爬虫设置
      - middlewares.py # 本项目中不需要更改
      - start.py # 启动爬虫，用于被sh脚本调用
      - /log # 日志文件，每次运行时更新，每天生成文件
      - /spiders
        - baidu.py # 爬虫
        - ...
      - /utils # 通用工具函数

爬取流程的核心从spiders文件夹中的爬虫文件开始,如baidu.py

1. start_url中的所有链接将作为爬取的起点(新闻门户)，将response传入parse()，进行分析
2. parse()获取页面中真正需要爬取的页面链接(放置在首页的各个新闻链接),传入parse_dir_contents()
3. parse_dir_contents()根据新的response析出需要的信息，填写item(从item=SpiderItem()获取)的属性，设置完成后发送给pipelines.py
4. 在pipeline中，对传入的item进行筛选、分析、修改，最终存入数据库

[回到目录](#yfnews新闻站说明文档)

### Web框架：flask

Flask是一个微型的 Python 开发的 Web 框架，基于Werkzeug WSGI工具箱和Jinja2 模板引擎。
本项目中，flask提供的主要功能是设置路由与渲染页面。
在Project/flasker/manage.py中，多次调用register_blueprint函数注册蓝图，每个蓝图都来自于一个py文件，以service包下的login为例：

```Python
    bp_login=Blueprint('login',__name__,url_prefix='/service')
    
    @bp_login.route('/login', methods=['POST'])
    def login():
        ...
        return ''
```

变量bp_login用于在manager.py中引入并注册
url_prefix是每个路由前自动添加的前缀，方便地管理通用部分
route的参数则决定在前缀之后，具体使用的路径
紧随其后定义的函数将处理对应请求
处理函数必须要有返回值，本项目中，对于前端页面则返回Jinja2渲染的html模板
启动服务器后，即可对'http://服务器ip:端口/service/login'发送请求

```Python
return render_template('/news/recommend.html', data=data[0], page_num=page_num,page=page, form=form)
```

[回到目录](#yfnews新闻站说明文档)

### html渲染引擎：Jinja2

Jinja2是基于python的html模板引擎，在flask框架中得到负则渲染页面
使用render_template可以如上自主设置参数，将后端处理的数据提供给html页面使用
html文件都存放在"yfnews/newsProject/flasker/templates/"之下，以render_template的首个参数为相对路径，即可找到对应的html文件
Jinja2引擎通过{{...}},{%...%}对html产生影响，在{{}}中，可以将变量值写到html文档中，而{%%}中可以设置循环控制语句等

```Jinja2
    {% for tag in news.tags %}  
        {% if loop.index<11 %}  
            <button type="button" class="btn btn-outline-info disabled">{{ tag }}</button>  
        {% endif %}  
    {% endfor %}
```

这段代码将根据news变量的tags属性，对其中每一个tag生成一个按钮，且以tag作为内容。但是最多只会生成10个
另外，在Jinja2中无法直接像python一样使用函数，而是"过滤器"充当了函数的角色：[Jinja2内置过滤器](https://jinja.palletsprojects.com/en/2.11.x/templates/#builtin-filters)
自定义filter则类似于设置页面路由，可以在任何蓝图中进行：

```Python
from flask import Blueprint
bp_filter = Blueprint('filter', __name__)
@bp_filter.app_template_filter('page_range')  
def page_range(page, page_num):  
    page = int(page)  
    page_num = int(page_num)  
    if page_num <= 5:  
        return [1, page_num]  
    else:  
        end = min(page + 2, page_num)  
        start = max(1, end - 4)  
        end = min(start + 4, page_num)  
    return [start, end]
```

将蓝图注册后，就可以使用过滤器了

```Jinja2
{% set range_list= page|page_range(page_num) %}
```

使用过滤器与函数的不同在于，参数并不都放在()中传入，而将第一个参数用|隔开放在过滤器左边
这行代码与python中page_range(page,page_num)等效

[回到目录](#yfnews新闻站说明文档)

### 文本分析：Jieba中文分词库

import jieba.analyse使用
本项目使用jieba库提供的TF-IDF、text rank两种关键词提取算法

TF-IDF：基于词频分析，文章中出现比例越大的词越是关键词。但同时认为越罕见的词越重要，避免提取与文章无关的常用词

```Python
jieba.analyse.extract_tags(sentence, topK=10, allowPOS=(['ns', 'n', 'vn']))
```

text rank：根据词之间的相邻关系构建网络，以PageRank算法迭代计算，认为rank排名靠前的词为关键词

```Python
jieba.analyse.textrank(sentence, topK=10, withWeight=False, allowPOS=('ns', 'n', 'vn'))
```

项目中，取两种算法所提取关键词的交集存入数据库

[回到目录](#yfnews新闻站说明文档)

## 数据结构

### 数据id

前9位为从2021-01-01 00：00经过的秒数

中2位为数据编号，目前的数据编号如下：

| 00   | 01   | 02      | 03           |
| ---- | ---- | ------- | ------------ |
| 新闻 | 用户 | session | 用户浏览历史 |

后5位位为区分同一秒多个id的标识

如id 42744490300002：
前9位4274449(这里只有7位是因为时间不够长)表示这条数据创建时距离2021-01-01 00:00 经过了4274449秒
其后2为03表示这是用户浏览历史的数据记录
最后五位的00002表示这是这一秒产生的第三条记录(0为第一条)

### tag常量表

对于标记文章的各种关键词，为快速检索，需要转化为数字储存

同时，只有人为认定具有重要意义的词，才有资格被转化为数字索引，所以需要记录tag-id的常量表

id由7位十进制组成，前2位标识类别，后5位为同类别下编号

常量表存放于yfnews/newsProject/flasker/static/tag_id/

有tag_category.csv tag_id.csv两张，每行由 <数字,字符串> 构成

tag_category记录<2位的id类别前缀,id类别>
tag_id记录<7位的具体id,tag名称>

[回到目录](#yfnews新闻站说明文档)

### newsTable结构

|          | _id              | abstract | author                                          | category                                          | content                          | stock                                               | score          | static_tags                          | tags           | time     | title    | url        | content_hash                                   | title_hash             |
| -------- | ---------------- | -------- | ----------------------------------------------- | ------------------------------------------------- | -------------------------------- | --------------------------------------------------- | -------------- | ------------------------------------ | -------------- | -------- | -------- | ---------- | ---------------------------------------------- | ---------------------- |
| 数据类型 | int64            | string   | int32或string                                   | int32或string                                     | array of string                  | int32                                               | array of int32 | string                               | datetime       | string   | string   | int64      | int64                                          |
| 含义     | 十进制16位数据id | 文章摘要 | 发布者，若收录进tag常量表则使用id，否则用字符串 | 新闻类型，若收录进tag常量表则使用id，否则用字符串 | 新闻内容，每个string表示一个段落 | 股票关键词，若收录进tag常量表则使用id，否则用字符串 | 新闻评分       | 已被常量表收录的关键词，将以数字存储 | 分析出的关键词 | 发布时间 | 新闻标题 | 新闻原网址 | 由内容计算出的去重索引(判断最长句是否hash冲突) | 由标题计算出的去重索引 |

### userTable结构

|          | _id              | email    | password                                         | permission                                      | salt                                 |
| -------- | ---------------- | -------- | ------------------------------------------------ | ----------------------------------------------- | ------------------------------------ |
| 数据类型 | int64            | string   | string                                           | int32                                           | int32                                |
| 含义     | 十进制16位数据id | 用户邮箱 | 用户输入的密码，md5加密一次后加盐，再进行md5加密 | 用户权限，1为普通，2为数据管理员，3为全能管理员 | [0,100000)的整数，是用于加密的密码盐 |

### historyTable结构

|          | _id              | news_id          | time                     | user_id          |
| -------- | ---------------- | ---------------- | ------------------------ | ---------------- |
| 数据类型 | int64            | int64            | datetime                 | int64            |
| 含义     | 十进制16位数据id | 十进制16位数据id | 历史信息载入数据库的时间 | 十进制16位数据id |

### tagIndexTable结构

|          | _id                          | tag_name | articles               |
| -------- | ---------------------------- | -------- | ---------------------- |
| 数据类型 | int32                        | String   | dict of int64          |
| 含义     | 唯一标识tag的十进制7位数据id | tag名字  | 存有此tag的news_id字典 |

### newsCacheTable结构

|          | _id                                                                             |
| -------- | ------------------------------------------------------------------------------- |
| 数据类型 | int64                                                                           |
| 含义     | 爬虫新爬取的news_id，与web模块通过数据库沟通，web模块不断地读取此表处理新增文章 |

[回到目录](#yfnews新闻站说明文档)

## 运维指南

项目根目录为yfnews文件夹

### mongodb启动与关闭

项目运行需要mongodb保持启动状态

1. 查询：$ sudo service mongodb status
2. 启动：$ sudo service mongodb start
3. 关闭：$ sudo service mongodb stop

### web模块的启动与关闭

启动：

1. $ cd newsProject/flasker 进入web模块
2. $ gunicorn -t 2400 -b 127.0.0.1:8000 manage:app 用gunicorn命令启动服务器，启动代码在manage.py中

关闭：

1. Ctrl+C 从运行状态中退出

### 爬虫模块的启动与关闭

启动：

1. $ sudo service cron start 启用crontab，每分钟调用爬虫
2. 如果由其他crontab任务，则使用 $ crontab -e 添加调用爬虫的命令，见[crontab设置](#crontab定时调用爬虫)

关闭：

1. $ sudo service cron stop 关闭crontab，停止调用爬虫
2. 如有其他crontab任务，则使用 $ crontab -e 删除调用爬虫的一行

### 常量表更新

1. 关闭web模块
2. $ cd newsProject/flasker 进入web模块目录
3. $ python3 unload.py 清空旧tag常量
4. 从根目录找到常量表文件夹：newsProject/flasker/static/tag_id/，修改两个csv文件内容
5. 回到flasker文件夹下，$ python3 reload.py 载入新的tag常量
6. $ gunicorn -t 2400 -b 127.0.0.1:8000 manage:app 重新启动服务器

[回到目录](#yfnews新闻站说明文档)

### 新增爬取网站

1. $ cd spider/spider 进入爬虫模块目录
2. 关闭爬虫模块
3. 在 spiders 目录下找到爬虫文件，新增xxx.py，添加下列代码

```Python
import logging
import scrapy
import os
import re
import datetime  # ['time']属性使用datetime类型


class XXXSpider(scrapy.Spider):
    name = 'xxx'
    allowed_domains = ['xxx.xxx']  # 这里填写域名限制，不在限制域名下的url不会爬取
    # 这里填写要爬取的源网站，如百度新闻财经栏目https://news.baidu.com/finance
    start_urls = ['url_1']

    def parse(self, response):
        logging.warning('尝试从'+'url_1'+'爬取')  # 输出日志

        # 下面使用xpath从原网站提取具体新闻页面的url
        ...
        for url in url_list:
            yield scrapy.Request(url, callback=self.parse_dir_contents)
    
    def parse_dir_content(self,response):
      item = SpiderItem()
      # 使用xpath提取信息
      ...
      item['title']=...
      item['author']=...
      item['category']=...
      item['stock']=...
      item['time']=...
      item['content']=... # content为String数组
      item['abstract']=... # abstract为content的至多前4段，如果超过60字则可以只取更少段数
      item['url']=response.url
      yield item
```

4. 使用response.xpath可从网页中提取上述，具体可参照spiders文件夹下的sina.py
5. 启动爬虫模块

### 修改爬虫日志输出

爬虫日志在yfnews/spider/spider/settings.py中进行配置：

```Python
LOG_LEVEL = "WARNING" # WARNING级以上的信息才输出，将默认输出的冗余信息过滤掉
log_file_path = "/.../yfnews/spider/spider/log/scrapy_{}_{}_{}.log".format(time_now.year, time_now.month, time_now.day) # /.../为服务器上到yfnews的绝对路径
LOG_FILE = log_file_path 
```

而日志的产生，既可以发生爬取流程的任何py文件中：

```Python
import logging
logging.warning(log_string) # 输出一个字符串到日志文件中
```

[回到目录](#yfnews新闻站说明文档)

### 部署到远程服务器

#### 环境安装

>需要保证python版本在3.6及以上，否则先升级python

安装mongodb

1. $ sudo apt-get install mongodb

安装scrpay依赖

1. $ pip3 install scrapy
2. $ pip3 install jieba
3. $ pip3 install pymongo

安装web依赖

1. $ pip3 install gunicorn
2. $ pip3 install eventlet
3. $ pip3 install gevent
4. $ pip3 install flask
5. $ pip3 install apscheduler
6. $ pip3 install pypinyin

>web模块同样依赖于pymongo，但已在scrpay依赖中安装，故不重复安装

#### 迁移数据库

1. 在原服务器用mongoexport命令备份数据文件(无需进入mongo窗口)
   1. $ mongoexport -d yanfuNewsDB -c newsTable -o <备份文件存放目录.json>
   2. $ mongoexport -d yanfuNewsDB -c userTable -o <备份文件存放目录.json>
   3. $ mongoexport -d yanfuNewsDB -c historyTable -o <备份文件存放目录.json>
   4. $ mongoexport -d yanfuNewsDB -c tagIndexTable -o <备份文件存放目录.json>
   5. $ mongoexport -d yanfuNewsDB -c newsCacheTable -o <备份文件存放目录.json>
2. 将备份文件发送到目标服务器
3. 在目标服务器用mongoimport命令载入备份数据文件
   1. $ mongoimport -d yanfuNewsDB -c newsTable --file <对应备份文件存放目录>
   2. $ mongoimport -d yanfuNewsDB -c userTable --file <对应备份文件存放目录>
   3. $ mongoimport -d yanfuNewsDB -c historyTable --file <对应备份文件存放目录>
   4. $ mongoimport -d yanfuNewsDB -c tagIndexTable --file <对应备份文件存放目录>
   5. $ mongoimport -d yanfuNewsDB -c newsCacheTable --file <对应备份文件存放目录>
4. 进入mongo命令窗口$ mongo
5. 切换到数据库use yanfuNewsDB
6. 构建索引
   1. db.newsTable.createIndex({'time':-1})
   2. db.historyTable.createIndex({'user_id':1})
   3. db.userTable.createIndex({'email':1})

#### 修改目录配置

编辑yfnews/spider/run.sh,将cd后内容改为yfnews/spider所在的绝对路径

```sh
#!/bin/bash
cd /home/zx/yfnews/spider
PYTHONPATH=./ python3 spider/start.py
echo "脚本执行完毕"
exit 0
```

#### crontab定时调用爬虫

1. $ crontab -e
2. 在最下方添加一行

```crontab
* * * * * flock -xn /.../yfnews/spider/crontab.lock -c 'sh /.../yfnews/spider/run.sh'
```

/.../为服务器上到yfnew的绝对路径

[回到爬虫模块的启动与关闭](#爬虫模块的启动与关闭)

[回到目录](#yfnews新闻站说明文档)

## http请求接口

### 注册

`${ip}:${port}/service/register`

方法：POST

输入参数

| 参数     | 类型   | 含义     | 必填 | 示例                |
| -------- | ------ | -------- | ---- | ------------------- |
| email    | string | 注册邮箱 | 是   | example@example.com |
| password | string | 注册密码 | 是   | abcd1234            |

输出参数

| 参数    | 类型   | 含义                               | 必填 | 示例                   |
| ------- | ------ | ---------------------------------- | ---- | ---------------------- |
| rtn     | int32  | 请求是否成功，1表示成功，0表示失败 | 是   | 1                      |
| message | string | 请求描述信息                       | 是   | '注册成功，可以登录了' |

### 登录

`${ip}:${port}/service/login`

方法：POST

输入参数

| 参数     | 类型   | 含义     | 必填 | 示例                |
| -------- | ------ | -------- | ---- | ------------------- |
| email    | string | 注册邮箱 | 是   | example@example.com |
| password | string | 注册密码 | 是   | abcd1234            |

输出参数

| 参数       | 类型   | 含义                               | 必填 | 示例                         |
| ---------- | ------ | ---------------------------------- | ---- | ---------------------------- |
| rtn        | int32  | 请求是否成功，1表示成功，0表示失败 | 是   | 1                            |
| message    | string | 请求描述信息                       | 是   | '登录失败，用户名或密码错误' |
| session_id | int64  | 本次登录的session_id               | 否   | 33412700200000               |

### 登出

`${ip}:${port}/service/logout`

方法：POST

输入参数

| 参数       | 类型  | 含义               | 必填 | 示例           |
| ---------- | ----- | ------------------ | ---- | -------------- |
| session_id | int64 | 要登出的session_id | 是   | 33412700200000 |

输出参数

| 参数    | 类型   | 含义                               | 必填 | 示例                       |
| ------- | ------ | ---------------------------------- | ---- | -------------------------- |
| rtn     | int32  | 请求是否成功，1表示成功，0表示失败 | 是   | 1                          |
| message | string | 请求描述信息                       | 是   | 'session_id错误，登出无效' |

[回到目录](#yfnews新闻站说明文档)

### 资讯推荐

`${ip}:${port}/service/recommend`

方法：GET或POST

输入参数

| 参数       | 类型  | 含义             | 必填            | 示例           |
| ---------- | ----- | ---------------- | --------------- | -------------- |
| page       | int32 | 库中检索的页数   | 否，缺省默认为1 | 10             |
| session_id | int64 | 根据登陆状态查询 | 是              | 33412700200000 |

输出参数

| 参数      | 类型        | 含义                               | 必填 | 示例 |
| --------- | ----------- | ---------------------------------- | ---- | ---- |
| rtn       | int32       | 请求是否成功，1表示成功，0表示失败 | 是   | 1    |
| post_data | json object | 查询到的新闻list                   | 是   |      |
| news_size | json object | 可推荐的新闻总数                   | 是   | 824  |

[回到目录](#yfnews新闻站说明文档)

### 全库检索

`${ip}:${port}/service/search`

方法：GET或POST

输入参数

| 参数         | 类型   | 含义                                       | 必填                         | 示例                      |
| ------------ | ------ | ------------------------------------------ | ---------------------------- | ------------------------- |
| page         | int32  | 库中检索的页数                             | 否，缺省默认为1              | 10                        |
| session_id   | int64  | 根据登陆状态查询                           | 是                           | 33412700200000            |
| search_words | String | 要查询的关键词,用'.'隔开(需存在于常量表中) | 否，缺省默认不限制关关键词   | '参考消息.环球网'         |
| order        | String | 结果排序方式                               | 否，缺省默认按时间从先近到远 | 'by_time'                 |
| time_range   | String | 时间范围限制                               | 否，缺省默认全域             | '2021/01/25 - 2021/02/23' |

排序方式选项：

1. by_time:按时间排序，近的在前
2. by_time_reverse:按时间排序，早发布的在前

输出参数

| 参数      | 类型        | 含义                               | 必填 | 示例       |
| --------- | ----------- | ---------------------------------- | ---- | ---------- |
| rtn       | int32       | 请求是否成功，1表示成功，0表示失败 | 是   | 1          |
| post_data | json object | 查询到的新闻list                   | 否   |            |
| news_size | json object | 库中新闻总数                       | 否   | 124        |
| message   | string      | 请求描述信息                       | 是   | '查询成功' |

说明：
搜索词在tag常量表时，返回包含词tag的新闻
搜索词不在tag常量表，则根据标题进行模糊搜索

[回到目录](#yfnews新闻站说明文档)

### 查看单条新闻

`${ip}:${port}/service/show`

方法：GET或POST

输入参数

| 参数       | 类型  | 含义               | 必填 | 示例           |
| ---------- | ----- | ------------------ | ---- | -------------- |
| session_id | int64 | 查看页面是是否登录 | 是   | 33412700200000 |
| news_id    | int64 | 新闻id             | 是   | 28844870000001 |

输出参数

| 参数      | 类型        | 含义                               | 必填             | 示例           |
| --------- | ----------- | ---------------------------------- | ---------------- | -------------- |
| rtn       | int32       | 请求是否成功，1表示成功，0表示失败 | 是               | 1              |
| post_data | json object | 查询到的新=新闻                    | 否，查询成功才有 |                |
| message   | string      | 请求描述信息                       | 是               | '获取新闻成功' |

[回到目录](#yfnews新闻站说明文档)

### 删除新闻

`${ip}:${port}/service/delete`

方法：GET或POST

输入参数

| 参数       | 类型  | 含义         | 必填 | 示例           |
| ---------- | ----- | ------------ | ---- | -------------- |
| session_id | int64 | 查看用户权限 | 是   | 33412700200000 |
| news_id    | int64 | 新闻id       | 是   | 28844870000001 |

输出参数

| 参数    | 类型   | 含义                               | 必填 | 示例                           |
| ------- | ------ | ---------------------------------- | ---- | ------------------------------ |
| rtn     | int32  | 请求是否成功，1表示成功，0表示失败 | 是   | 1                              |
| message | string | 请求描述信息                       | 是   | '权限不足，只有管理员可以修改' |

[回到目录](#yfnews新闻站说明文档)

### 删除标签

`${ip}:${port}/service/delete_tag`

方法：GET或POST

输入参数

| 参数       | 类型   | 含义         | 必填 | 示例           |
| ---------- | ------ | ------------ | ---- | -------------- |
| session_id | int64  | 查看用户权限 | 是   | 33412700200000 |
| news_id    | int64  | 新闻id       | 是   | 28844870000001 |
| tag_name   | string | 要删除的tag  | 是   | 信息化         |

输出参数

| 参数    | 类型   | 含义                               | 必填 | 示例                           |
| ------- | ------ | ---------------------------------- | ---- | ------------------------------ |
| rtn     | int32  | 请求是否成功，1表示成功，0表示失败 | 是   | 1                              |
| message | string | 请求描述信息                       | 是   | '权限不足，只有管理员可以修改' |

### 添加标签

`${ip}:${port}/service/add_tag`

方法：GET或POST

输入参数

| 参数       | 类型   | 含义         | 必填 | 示例           |
| ---------- | ------ | ------------ | ---- | -------------- |
| session_id | int64  | 查看用户权限 | 是   | 33412700200000 |
| news_id    | int64  | 新闻id       | 是   | 28844870000001 |
| tag_name   | string | 要添加的tag  | 是   | 信息化         |

输出参数

| 参数    | 类型   | 含义                               | 必填 | 示例                           |
| ------- | ------ | ---------------------------------- | ---- | ------------------------------ |
| rtn     | int32  | 请求是否成功，1表示成功，0表示失败 | 是   | 1                              |
| message | string | 请求描述信息                       | 是   | '权限不足，只有管理员可以修改' |

### 修改从新闻作者、类别、股票代码

`${ip}:${port}/service/change_infochange_info`

方法：GET或POST

输入参数

| 参数       | 类型   | 含义             | 必填 | 示例           |
| ---------- | ------ | ---------------- | ---- | -------------- |
| session_id | int64  | 查看用户权限     | 是   | 33412700200000 |
| news_id    | int64  | 新闻id           | 是   | 28844870000001 |
| author     | string | 要修改的发布者   | 是   | 人民日报       |
| category   | string | 要修改的类别     | 是   | 财经           |
| stock      | string | 要修改的股票代码 | 是   | 股票占位符     |

输出参数

| 参数    | 类型   | 含义                               | 必填 | 示例                           |
| ------- | ------ | ---------------------------------- | ---- | ------------------------------ |
| rtn     | int32  | 请求是否成功，1表示成功，0表示失败 | 是   | 1                              |
| message | string | 请求描述信息                       | 是   | '权限不足，只有管理员可以修改' |

[回到目录](#yfnews新闻站说明文档)

### 爬虫专用接口：新增文章tag转化为id，修改倒排索引表

方法：POST

输入参数

| 参数    | 类型   | 含义                 | 必填 | 示例           |
| ------- | ------ | -------------------- | ---- | -------------- |
| key     | String | 爬虫专用接口验证口令 | 是   |                |
| news_id | int64  | 新闻id               | 是   | 28844870000001 |

输出参数

| 参数    | 类型   | 含义                               | 必填 | 示例                                              |
| ------- | ------ | ---------------------------------- | ---- | ------------------------------------------------- |
| rtn     | int32  | 请求是否成功，1表示成功，0表示失败 | 是   | 1                                                 |
| message | string | 请求描述信息                       | 是   | 'key口令错误，此接口仅供爬虫模组调用，请查看文档' |

说明：
此接口专供爬虫调用，在爬取新文章后通知服务器进行增量处理
需要提供key='YanFuNews_NewsTable'才能正常使用，一般情况下不应人为调用

[回到目录](#yfnews新闻站说明文档)