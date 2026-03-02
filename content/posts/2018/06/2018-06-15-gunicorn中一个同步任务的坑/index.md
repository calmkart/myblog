---
title: "gunicorn中一个同步任务的坑"
date: 2018-06-15
description: "最近有些django定时任务要跑，又懒的做异步celery worker tasks了，就是普通的同步任务，用的django crontab，其中django用的是gunicorn-nginx的部署方式。但几天下来..."
categories:
  - "计算机"
tags:
  - "django"
  - "gunicorn"
---

最近有些django定时任务要跑，又懒的做异步celery worker tasks了，就是普通的同步任务，用的django crontab，其中django用的是gunicorn->nginx的部署方式。但几天下来，发现任务总是执行到一半就停了，排错发现一个偶尔会出现的坑



...

<!--more-->

检测到用curl请求接口，每到31秒就停止，后续同步任务不再继续

检查gonicorn参数，发现默认的timeout值为30s，既客户端请求30s后超时

gunicorn启动参数加上     -t 120

问题解决

...

<div class="archived-comments">

<h2>历史评论 (2 条)</h2>
<p class="comment-notice">以下评论来自原 WordPress 站点，仅作存档展示。</p>
<div class="comment-item">
<div class="comment-meta"><strong>wuyan</strong> (2019-07-29 16:34)</div>
<div class="comment-body">gunicorn启动参数加上  -t 120 是表示120s超时吗？如果是的话，会不会执行到120s就停了，还是没有解决根本问题吧？</div>
</div>
<div class="comment-item comment-reply">
<div class="comment-meta"><strong>calmkart</strong> (2019-08-09 15:26)</div>
<div class="comment-body">本来就是个简单的定时任务,要想彻底解决问题用celery做异步队列处理啊</div>
</div>
</div>
