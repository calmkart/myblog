---
title: "NFS搭建及端口安全控制"
date: 2017-12-05
description: "NFS服务用于文件分享和文件同步，功能就不描述了，架构是C/S的模式 一.简单配置 1.服务端 测试：showmount -e"
categories: 
  - "计算机"
tags: 
  - "运维"
  - "运维安全"
---

NFS服务用于文件分享和文件同步，功能就不描述了，架构是C/S的模式

一.简单配置

1.服务端

```bash
apt install nfs-kernel-server
vi /etc/exports
########添加如下#######
/opt/nfs *(ro,sync,no_subtree_check)
#NFS共享路径 IP(只读，同步，不检查父目录)

```

```bash
service nfs-kernel-server restart 
service rpcbind restart

```

测试：showmount -e <!--more-->

2.客户端

```bash
apt-get install nfs-common
mount 远程nfs_ip:/路径 /本地路径

```



二.NFS服务端口控制

服务端配置：

```bash
# /etc/default/nfs-common
 STATDOPTS="--port 32765 --outgoing-port 32766"

 # /etc/default/nfs-kernel-server
 RPCMOUNTDOPTS="-p 32767"

 # /etc/default/quota
 RPCRQUOTADOPTS="-p 32769"

```

```bash
 # /etc/sysctl.conf
fs.nfs.nfs_callback_tcpport = 32764
fs.nfs.nlm_tcpport = 32768
fs.nfs.nlm_udpport = 32768

```

```bash
sysctl --system
service nfs-kernel-server restart
service rpcbind restart

```

则可以将服务端端口限制为:

2049,111,32764-32769 TCP/UDP

<div class="archived-comments">

<h2>历史评论 (1 条)</h2>
<p class="comment-notice">以下评论来自原 WordPress 站点，仅作存档展示。</p>
<div class="comment-item">
<div class="comment-meta"><strong>孙昊</strong> (2017-12-05 16:49)</div>
<div class="comment-body">我日，彭总屌炸了</div>
</div>
</div>
