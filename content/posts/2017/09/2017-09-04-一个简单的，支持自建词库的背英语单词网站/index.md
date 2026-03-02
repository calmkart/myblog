---
title: "一个简单的，支持自建词库的背英语单词网站"
date: 2017-09-04
description: "由于近来在学英语，需要背英语单词。但网上背英语单词的网站好像不花钱都不支持自建词库，所以就顺手自己写了一个简单而支持自建词库的背英语单词网站，自用。(www.calmkart.com/learn)"
categories: 
  - "计算机"
tags: 
  - "bootstrap"
  - "flask"
  - "jinja2"
  - "python"
  - "sql"
  - "sqlite3"
---

由于近来在学英语，需要背英语单词。但网上背英语单词的网站好像不花钱都不支持自建词库，所以就顺手自己写了一个简单而支持自建词库的背英语单词网站，自用。([www.calmkart.com/learn](http://www.calmkart.com/learn)) <!--more-->

首先需要解决的问题是英语单词的翻译过程，我的第一反应是考虑用GOOGLE翻译的API，但是经过查询，需要收费，国内的大多在线翻译的API一般也都是要收费的。 然后开始考虑用爬网页的方式去做，但因为GOOGLE有自己的防爬机制(token)，通过本地计算后再爬网页的话也比较麻烦，浪费时间。 所以最后采取了使用本地词典数据库的方法来做翻译。

最复杂的地方是PYTHON中字符编码的问题，需要很多次无谓ENCODE和DECODE，于是我采用了最简单的方法，完全放弃使用python2.7，而直接采用python3.6，很好的解决了字符编码的问题。剩下的后端的东西都比较简单，无非上传查找翻译等等，见后文的代码地址。

主要页面功能如下： ![](images/1.jpg) ![](images/2.jpg)

前后端数据交互采用了由后端渲染的方式，用了flask的jinja2模板。



这里采用jinja2模板渲染之后又一个可以考虑的地方，是用户每次切换一个单词就去服务器查询一次结果还是服务器直接查询出该用户字典所有单词结果直接传给用户，用户切词等于完全在本地通过JS操作，和服务器完全脱离关系。 在这里采用了后一种方式，直接把用户词典的所有翻译结果传给客户端，然后用户切词完全依靠JS操作，不需要再去服务器做查询，这样应该是比较快的，而且也能给服务器减轻负担。

前端是采用了bootstrap框架，bootstrap的布局是分成12格，挺好用的。

项目地址：[www.calmkart.com/learn](http://www.calmkart.com/learn)

代码已上传github,地址：

[https://github.com/calmkart/learn_english](https://github.com/calmkart/learn_english)

自行使用时请先修改setting文件中的路径，用于与本地匹配。

<div class="archived-comments">

<h2>历史评论 (1 条)</h2>
<p class="comment-notice">以下评论来自原 WordPress 站点，仅作存档展示。</p>
<div class="comment-item">
<div class="comment-meta"><strong>郭昊旻</strong> (2017-09-08 15:54)</div>
<div class="comment-body">我日，这个功能屌，强无敌，妈妈再也不用担心我的英语了。</div>
</div>
</div>
