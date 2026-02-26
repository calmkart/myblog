---
title: "为django-admin的userpermission添加read only(can view)权限"
date: 2018-09-06
categories: 
  - "计算机"
tags: 
  - "django"
  - "django-admin"
  - "权限系统"
  - "运维开发"
---

默认的django-admin中用户的models权限只有三个,分别是(Can change, Can add, Can delete),显然的,对于绝大部分crud工程师(^\_^)而言,一眼看过去就少了些什么,没错,少了很关键的Can view权限.

当然django-admin的用户权限是可以自定义的,需要改permission的meta,这里不细述,发现一个简单好用的django app,可以直接添加Can view权限,美滋滋.

最终效果如下 [![](images/B6CE8AA0-F925-4290-B2C0-E3C98ECF0C79.png)](http://www.calmkart.com/wp-content/uploads/2018/09/B6CE8AA0-F925-4290-B2C0-E3C98ECF0C79.png) <!--more-->

插件是: django-admin-view-permission 地址 [https://github.com/ctxis/django-admin-view-permission](https://github.com/ctxis/django-admin-view-permission) 使用方式及其简单

```
#pip安装插件
pip install django-admin-view-permission

#将app注册,记得一定注册在django.contrib.admin之前
INSTALLED_APPS = [
    'admin_view_permission',
    'django.contrib.admin',
    ...
]

#更新数据库
python manage.py migrate

即可

#如需要只对一些数据库管用,可以
ADMIN_VIEW_PERMISSION_MODELS = [
    'auth.User',
    ...
]

```

的确是个好东西啊,免掉了手写这种本应就有的权限.分享一下.
