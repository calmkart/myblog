---
title: "saltstack的安装和基本使用"
date: 2017-11-29
categories: 
  - "计算机"
tags: 
  - "saltstack"
  - "自动化"
  - "运维"
  - "集群管理"
---

saltstack可用于批量管理集群,用的是c/s架构，master管理多个minion

测试系统：debian8.7

**一.安装master**

1.添加apt key

```
wget -O - https://repo.saltstack.com/apt/debian/8/amd64/latest/SALTSTACK-GPG-KEY.pub | sudo apt-key add -
```

<!--more--> 2.将saltstack源添加进apt源

```
vi /etc/apt/sources.list
#添加saltstack源
deb http://repo.saltstack.com/apt/debian/8/amd64/latest jessie main
```

3.更新apt

```
apt-get update
```

4.安装master端相关组件

```
apt-get install salt-api
apt-get install salt-cloud
apt-get install salt-master
apt-get install salt-minion
apt-get install salt-ssh
apt-get install salt-syndic

```

5.配置master

```
vi /etc/salt/master
####################常见配置如下####################
#指定master，冒号后有一个空格
user: root
#自动接收minion
auto_accept: True

#-------以下为可选--------------
#自动接收minion
auto_accept: True
#salt的运行线程，开的线程越多一般处理的速度越快，但一般不要超过CPU的个数
worker_threads: 10
# master的管理端口
publish_port : 4505
# master跟minion的通讯端口，用于文件服务，认证，接受返回结果等
ret_port : 4506
# 如果这个master运行的salt-syndic连接到了一个更高层级的master,那么这个参数需要配置成连接到的这个高层级master的监听端口
syndic_master_port : 4506
# 指定pid文件位置
pidfile: /var/run/salt-master.pid
# saltstack 可以控制的文件系统的开始位置
root_dir: /
# 日志文件地址
log_file: /var/log/salt_master.log
# 分组设置
nodegroups:
  group_all: '*'
# salt state执行时候的根目录
file_roots:
  base:
    - /srv/salt/
# 设置pillar 的根目录
pillar_roots:
  base:
    - /srv/pillar
```

6.启动master

```
systemctl start salt-master
```

**二.安装minion**

1.安装salt-minion

```
apt-get install salt-minion
```

2.配置minion相关信息

```
vi /etc/salt/minion

###################以下为常见设置###########################
#指定master，冒号后有一个空格
master: 10.32.80.121

#-------以下为可选--------------
# minion的识别ID，可以是IP，域名，或是可以通过DNS解析的字符串
id: xx
# salt运行的用户权限
user: root
# master的识别ID，可以是IP，域名，或是可以通过DNS解析的字符串
master : ip
# master通讯端口
master_port: 4506
# 备份模式，minion是本地备份，当进行文件管理时的文件备份模式
backup_mode: minion
# 执行salt-call时候的输出方式
output: nested 
# minion等待master接受认证的时间
acceptance_wait_time: 10
# 失败重连次数，0表示无限次，非零会不断尝试到设置值后停止尝试
acceptance_wait_time_max: 0
# 重新认证延迟时间，可以避免因为master的key改变导致minion需要重新认证的syn风暴
random_reauth_delay: 60
# 日志文件位置
log_file: /var/logs/salt_minion.log
# 文件路径基本位置
file_roots:
  base:
    - /etc/salt/minion/file
# pillar基本位置
pillar_roots:
  base:
    - /data/salt/minion/pillar
```

3.启动minion

```
systemctl start salt-minion
```

**三.通过master管理minion**

1.配置key

```
#查看当前所有的key
salt-key

#注册所有key
salt-key -A

#注册某个key
salt-key -a minion_id

#删除全部key
salt-key -D

#删除某个key
salt-key -d minion_id
```

2.测试是否连通

```
#测试所有minion的连通性
salt '*' test.ping

#测试某个minion的连通性
salt 'minion_id' test.ping
```

3.常用命令

```
#salt cmd.run用于让minion批量执行命令
salt '*' cmd.run 'ifconfig'
salt 'minion_id' cmd.run 'ifconfig'

#salt-run manage查看minioni信息
salt-run manage.status #查看所有minion状态
salt-run manage.down ##查看down掉的minion
salt-run manage.up ##查看up的minion

#salt-key管理密钥
salt-key [options]
salt-key -L              ##查看所有minion-key
salt-key -a <key-name>   ##接受某个minion-key
salt-key -d <key-name>   ##删除某个minion-key
salt-key -A              ##接受所有的minion-key
salt-key -D              ##删除所有的minion-key

#salt-call在minion上执行某命令
salt-call [options] <function> [arguments]
salt-call test.ping           ##自己执行test.ping命令
salt-call cmd.run 'ifconfig'  ##自己执行cmd.run函数

#salt-cp分发文件给minion(不支持目录分发)
salt-cp '*' testfile.html /tmp   #把testfile.html发送到所有minion的/tmp文件夹
salt-cp 'test*' index.html /tmp/a.html   #把index.html发送到所有test*的minion并重命名为/tmp/a.html

#目标minion分组
修改/etc/salt/master
nodegroups:
  testgroup1: 'L@test82.salt.cn,test83.salt.cn'
  testgroup2: '192.168.2.84'
#-N为分组命令符
salt -N testgroup1 test.ping
#分组分为多种类型：
    G -- 针对 Grains 做单个匹配，例如：G@os:Ubuntu
    E -- 针对 minion 针对正则表达式做匹配，例如：E@web\d+.(dev|qa|prod).loc
    P -- 针对 Grains 做正则表达式匹配，例如：P@os:(RedHat|Fedora|CentOS)
    L -- 针对 minion 做列表匹配，例如：L@minion1.example.com,minion3.domain.com or bl*.domain.com
    I -- 针对 Pillar 做单个匹配，例如：I@pdata:foobar
    S -- 针对子网或是 IP 做匹配，例如：S@192.168.1.0/24 or S@192.168.1.100
    R -- 针对客户端范围做匹配，例如： R@%foo.bar

```
