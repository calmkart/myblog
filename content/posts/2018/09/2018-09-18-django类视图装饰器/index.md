---
title: "django类视图装饰器"
date: 2018-09-18
description: "一点关于django类视图装饰器的小笔记。 django类视图是很常用的，对于传统的函数视图来说，装饰器可以直接装饰函数，但类视图，装饰器无法直接装饰类方法。 比较了几种常见的解决方法,个人觉得比较优雅的解决方法如下："
categories: 
  - "计算机"
tags: 
  - "django"
  - "python"
  - "类视图"
  - "运维开发"
---

一点关于django类视图装饰器的小笔记。

django类视图是很常用的，对于传统的函数视图来说，装饰器可以直接装饰函数，但类视图，装饰器无法直接装饰类方法。

比较了几种常见的解决方法,个人觉得比较优雅的解决方法如下：

```python
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

@method_decorator(csrf_exempt, name="dispatch")
class login(View):

    @method_decorator(auth_login)
    def get(self, request, username):
        #....func...
        return render(request, 'login.html', {"displayName":username, "admin_flag":admin_flag})

```

<!--more-->

既如以上代码，将装饰器函数传给method_decorator方法，直接修饰视图类方法。

也可直接修饰视图类，对于需要修饰的方法，用name参数的形式传入method_decorator中即可，但感觉不够优雅。

```python
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(auth_login, name="get")
class login(View):

    def get(self, request, username):
        #....func...
        return render(request, 'login.html', {"displayName":username, "admin_flag":admin_flag})

```

需要稍微注意的是，csrf_exempt跨站排除装饰器，只能修饰在类视图的dispatch方法上，既原始写法如下：

```python
class login(View):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(login,self).dispatch(request,*args,**kwargs)
    
    def get(self, request, username):
        #....func...
        return render(request, 'login.html', {"displayName":username, "admin_flag":admin_flag})

```

但其实直接用类方法装饰器装饰视图类，传入参数name=dispatch就行了，不需要重写dispatch方法。

既如上文。

<div class="archived-comments">

<h2>历史评论 (2 条)</h2>
<p class="comment-notice">以下评论来自原 WordPress 站点，仅作存档展示。</p>
<div class="comment-item">
<div class="comment-meta"><strong>( 曰..曰 )</strong> (2018-09-19 16:06)</div>
<div class="comment-body">大佬，大佬，这绝对是大佬</div>
</div>
<div class="comment-item comment-reply">
<div class="comment-meta"><strong>calmkart</strong> (2018-09-20 19:02)</div>
<div class="comment-body">总裁谢你说大佬就大佬好吧</div>
</div>
</div>
