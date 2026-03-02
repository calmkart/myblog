---
title: "关于supervisor/gosuv等控制django/flask进程的小贴士"
date: 2018-02-11
description: "使用supervisor/gosuv等控制django/flask进程时端口占用导致重启失败的解决方案。"
categories: 
  - "计算机"
tags: 
  - "django"
  - "flask"
  - "gosuv"
  - "supervisor"
---

在使用supervisor/gosuv等进程控制程序控制django/flask进程时，常常会出现一个"BUG"------输入supervisor restart {app}/gosuv stop/start {app}后，经常会出现django/flask重启失败，因为端口已占用的错误。

<!--more-->

这里我们常常想到，先把端口关掉不就可以了？经常在代码中加入如下命令：(如果程序是django或者flask，占用的端口是82端口)

```python
import subprocess
import os

pid = os.popen("lsof -i:82|grep python|awk '{print $2}'").read()
if len(pid):
    subprocess.check_output("kill -9 "+str(int(pid)), shell=True)
#注意，这里一定要用subprocess库来kill进程。用os.system运行kill -9或os.kill()都会导致新进程产生
```

这样虽然可行，但是比较麻烦。其实占用端口的原因是flask/django服务器自动reload造成的，只需要在supervisor/gosuv的启动指令里，加上--noreload参数就不会产生这个"BUG"了，举例如下：

```bash
#原来启动指令
python manage.py runserver 0.0.0.0:82
#更新启动指令
python manage.py runserver 0.0.0.0:82 --noreload
```

搞定
