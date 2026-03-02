---
title: "修改github项目所属语言"
date: 2018-09-25
description: "github上项目统计是以最多的语言作为项目语言,有时候有点为难强迫症. 以下方法可以改变统计的语言,一点小笔记 搞定!"
categories: 
  - "计算机"
tags: 
  - "github"
---

github上项目统计是以最多的语言作为项目语言,有时候有点为难强迫症. 以下方法可以改变统计的语言,一点小笔记

<!--more-->

```text
#创建.gitattributes文件在项目根目录,内容如下
*.css linguist-language=Python
*.less linguist-language=Python
*.js linguist-language=Python
*.html linguist-language=Python

```

搞定!
