---
title: "sshd的AuthorizedKeysCommand选项"
date: 2018-08-22
categories: 
  - "计算机"
tags: 
  - "pub_key"
  - "ssh"
  - "跳板机"
---

通常机器上保存的key都是读取~/.ssh/authorized\_keys文件来获取的,这样的话就不好做到动态调整和控制权限.

openssh6.2版本以上新增加了AuthorizedKeysCommand选项功能,可以获取动态keys列表

<!--more-->

```
Port 22
Protocol 2
SyslogFacility AUTH
LogLevel INFO

#PermitRootLogin no

RSAAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile      .ssh/authorized_keys

# To disable tunneled clear text passwords, change to no here!
PasswordAuthentication no

# Change to no to disable s/key passwords
ChallengeResponseAuthentication no

UsePAM yes

AllowTcpForwarding no
X11UseLocalhost no
UseDNS no
Subsystem       sftp    /usr/libexec/openssh/sftp-server

AuthorizedKeysCommand /etc/get_key.sh
AuthorizedKeysCommandUser root

```

一个典型的sshd配置如上,其中AuthorizedKeysCommand选项的作用是在每次登录时都调用指定的脚本，并以脚本当前的输出作为keys列表.当脚本的输出为空时,再调用本地authorized\_keys文件中的keys列表验证.

一个典型的使用方式是,将ssh公钥放在一个统一的鉴权服务器上,与cmdb中的服务器资源列表做匹配,通过http restapi返回服务器允许登录的公钥列表,在服务器上通过get\_key.sh进行读取.当读取为空时，使用本地authorized\_keys，一般为权限用户.

这样就可以很好的实现服务器授权，组授权以及跳板机相关功能.(本地key转发通过跳板机连接服务器的情况,就可以做到权限集中与鉴权了)
