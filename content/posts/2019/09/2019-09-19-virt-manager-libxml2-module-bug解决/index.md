---
title: "virt-manager libxml2 module bug解决"
date: 2019-09-19
description: "virt-manager是一个kvm的管理工具，在自己用的小型环境里还是很方便的，我也用了挺久。因为是mac所以是用homebrew-virt-manager。之前一直用的老版本，最近mac更新..."
categories: 
  - "计算机"
tags: 
  - "virt-manager"
---

[virt-manager](https://github.com/virt-manager/virt-manager)是一个kvm的管理工具，在自己用的小型环境里还是很方便的，我也用了挺久。因为是mac所以是用[homebrew-virt-manager](https://github.com/jeffreywildman/homebrew-virt-manager)。之前一直用的老版本，最近mac更新，而且老版本有存储池无法从/var/lib/libvirt/里切换的bug，所以通过brew更新到了最新的2.2.1版本，就出现了 **No module named 'libxml2'**  的bug，通过google和官方issue找不到解决办法，最终自己解决，这里记录一下，方便其他需要的朋友查询。 <!--more-->

主要的症状是brew安装或者更新完成homebrew-virt-manager后，运行virt-manager会显示

```bash
File "/usr/local/Cellar/virt-manager/2.2.1_2/libexec/share/virt-manager/virtinst/xmlapi.py", line 7, in <module>
    import libxml2
ModuleNotFoundError: No module named 'libxml2'
```

原因是默认的包从python2升级到了python3。

我们首先安装python3的libxml2包

```bash
pip3 install libxml2-python3
```

然后查询安装位置

```python
➜  ~ python3
Python 3.7.1 (default, Nov  6 2018, 18:49:54)
[Clang 9.0.0 (clang-900.0.39.2)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import libxml2
>>> print(libxml2.__file__)
/usr/local/lib/python3.7/site-packages/libxml2.py
```

然后将libxml2包和相关包从系统python3的默认site-packages拷贝到virt-manager的site-packages中即可

参考上面显示的路径，既是将

**/usr/local/lib/python3.7/site-packages/libxml\*** 

拷贝到

**/usr/local/Cellar/virt-manager/2.2.1_2/libexec/lib/python3.7/site-packages**

```python
cp -r /usr/local/lib/python3.7/site-packages/libxml* /usr/local/Cellar/virt-manager/2.2.1_2/libexec/lib/python3.7/site-packages
```

 

TIPS:

1，注意要拷贝libxml\*而不仅仅是libxml2.py，因为libxml2还依赖libxml2mod。拷贝少了还是会报找不到包。

2，我们也可以将python3的package添加到默认PYTHONPATH中去，也可以解决这个问题。

3，顺便记录一个virt / virt-manager使用的问题，更换默认存储池后新建的默认存储池必须设置名称为default，不然会自动在/var/lib/libvirt/目录下重建默认存储池

<div class="archived-comments">

<h2>历史评论 (1 条)</h2>
<p class="comment-notice">以下评论来自原 WordPress 站点，仅作存档展示。</p>
<div class="comment-item">
<div class="comment-meta"><strong>huku</strong> (2019-09-20 19:26)</div>
<div class="comment-body">非常感谢，前几个月碰到同样的问题了，一直没找到解决方法</div>
</div>
</div>
