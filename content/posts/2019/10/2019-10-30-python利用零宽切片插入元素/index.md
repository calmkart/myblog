---
title: "python利用零宽切片插入元素"
date: 2019-10-30
description: "常见的python插入元素方式一般是insert或者手动挪动后修改值,然后其实还有种比较少用的通过零宽切片插入元素的方式,比较有意思,随便记录下. 无正文. --"
categories: 
  - "计算机"
tags: 
  - "python"
---

常见的python插入元素方式一般是insert或者手动挪动后修改值,然后其实还有种比较少用的通过零宽切片插入元素的方式,比较有意思,随便记录下.

<!--more-->

```python
Python 3.8.0 (v3.8.0:fa919fdf25, Oct 14 2019, 10:23:27) 
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> a = [1,2,3,4,5]
>>> a[:0] = [0,0,0]
>>> a
[0, 0, 0, 1, 2, 3, 4, 5]
>>> a[4:4] = [8,8,8,8,8,8]
>>> a
[0, 0, 0, 1, 8, 8, 8, 8, 8, 8, 2, 3, 4, 5]
>>> a[4:8] = []
>>> a
[0, 0, 0, 1, 8, 8, 2, 3, 4, 5]

```

无正文.

<div class="archived-comments">

<h2>历史评论 (1 条)</h2>
<p class="comment-notice">以下评论来自原 WordPress 站点，仅作存档展示。</p>
<div class="comment-item">
<div class="comment-meta"><strong>_</strong> (2019-10-30 19:30)</div>
<div class="comment-body">a := int[]{1,2,3,4,5} b := int[]{0,0,0} c := make([]int, len(a)+len(b)) cnt := copy(c, b) copy(c[cnt:], a) fmt.Println(c) 跟Python比起来，go真是蠢透了, python的零宽切片插入元素跟php的array_splice()函数很像</div>
</div>
</div>
