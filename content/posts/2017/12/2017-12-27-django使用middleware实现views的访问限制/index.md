---
title: "django使用middleware实现views的访问限制"
date: 2017-12-27
categories: 
  - "计算机"
tags: 
  - "django"
  - "python"
  - "运维开发"
---

需要实现这样的需求，对于以个django app，需要对其中的一些restful api做IP访问限制，这样实现起来最方便的是在middleware中写逻辑。

关于django中间件的说明： [http://usyiyi.cn/translate/Django\_111/topics/http/middleware.html](http://usyiyi.cn/translate/Django_111/topics/http/middleware.html) [http://python.usyiyi.cn/translate/django\_182/topics/http/middleware.html](http://python.usyiyi.cn/translate/django_182/topics/http/middleware.html) <!--more-->

在django app得middleware.py中添加如下代码

```
from django.http import HttpResponse

class checkIPMiddleware(object):
    def process_request(self, request):
        root_func = request.path.split("/")[1]
        api_flag = True if root_func=="api" else False
        if api_flag:
            ip = request.META.get("HTTP_X_REAL_IP", request.META.get("REMOTE_ADDR"))
            if (ip=="10.10.10.10" or ip=="11.11.11.11"):
                return None
            else:
                return HttpReponse("you are not allowed")
        return None

```

关于request对象内容，详情如下(本代码限制的是所有/api/后的访问)： [http://python.usyiyi.cn/translate/django\_182/ref/request-response.html](http://python.usyiyi.cn/translate/django_182/ref/request-response.html)

关于获取用户IP，在没有反向代理的情况下可以获取http头中的REMOTE\_ADDR字段，用request.META对象来获取 当有Nginx等反向代理的时候，就会获取到本机IP，所以需要在nginx反向代理时，将用户原IP记录下来写入HTTP头中 既配置nginx配置如下(/site-enable/default):

```
location .... {    
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_set_header X-NginX-Proxy true;
}
```

最后在settings.py中将这个class添加进去

```
MIDDLEWARE_CLASSES = [
        'appname.middleware.checkIPMiddleware'
]
```

重启django之后，则/api后的restful api只允许10.10.10.10和11.11.11.11访问，其他时候就会返回"you are not allowed"
