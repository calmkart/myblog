---
title: "[django笔记]crontab,异常捕获和打印log"
date: 2018-05-28
description: "记录一些django常见功能的用法。 这次主要关注点是crontab定时任务,django/python的异常捕获,以及django/python的打印log功能"
categories:
  - "计算机"
---

记录一些django常见功能的用法。 这次主要关注点是crontab定时任务,django/python的异常捕获,以及django/python的打印log功能 <!--more-->

#### 一.crontab定时任务

首先安装djanto-crontab模块

```bash
pip install django-crontab
```

然后在django项目的settings.py里添加django-crontab模块

```python
INSTALLED_APPS = [
    ...,
    'django_crontab',
]
```

然后编写相关的cron定时任务程序，一般放在project/app/views里，命名为cron.py

接着在settings.py里添加定时任务

```python
CRONJOBS = [
    ('0 12 1 * *', 'app.views.cron.cron1'),
    ('0 12 * * 1-5', 'app.views.cron.cron2'),
]
```

定时设置参数为 (分 小时 日 月 星期),具体可参考google资料

然后常见的执行命令如下:

```bash
#查看定时任务
python manage.py crontab show

#添加定时任务(修改定时任务)
python manage.py crontab add

#删除定时任务
python manage.py crontab remove

#执行一次定时任务
python manage.py crontab run {定时任务id}

```

_**特别注意:crontab的log地址一定要写绝对路径**_

#### 二.django/python的错误捕获

###### 1.基础语法

```python
try:
    pass
except:
    pass
```

###### 2.常见异常类型

- AttributeError     试图访问一个对象没有的树形，比如foo.x,但foo没有属性x
- IOError         输入输出异常；基本是无法打开文件错误
- ImportError      无法引入模块或者包；基本上是路径问题或者名称错误
- IndentationError   语法错误；代码没有正确的对齐
- IndexError:       下标索引超出序列边界，比如当x只有三个元素，却试图访问x\[5\]
- KeyError         试图访问字典里不存在的键
- NameError        使用一个还未赋值的变量
- SyntaxError       代码非法，
- TypeError        传入对象类型与要求的不符合
- ValueError       传给函数的参数类型不正确,比如给int()函数传入字符串形

###### 3.通用错误类型

Exception

语法:

```python
except Exception:
```

或者:

```python
except Exception as e:
```

###### 4.traceback获取异常详情

```python
import traceback

#返回错误字符串
traceback.format_exc()
#打印错误字符串
traceback.print_exc()
 
#配合logging模块使用
logging.getLogger().error(traceback.format_exc())
```

#### 三.django/python的log打印

...

<div class="archived-comments">

<h2>历史评论 (1 条)</h2>
<p class="comment-notice">以下评论来自原 WordPress 站点，仅作存档展示。</p>
<div class="comment-item">
<div class="comment-meta"><strong>吴伟康</strong> (2018-06-08 17:24)</div>
<div class="comment-body">楼主你好，请问下如果异常没有被捕获，例如忘记定义这种类型的异常，该怎么避免这种情况的报错啊，不胜感激</div>
</div>
</div>
