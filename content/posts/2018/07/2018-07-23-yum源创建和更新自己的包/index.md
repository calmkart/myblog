---
title: "yum源创建和更新自己的包"
date: 2018-07-23
description: "以tengine为例，记录添加yum自用打包过程."
categories:
  - "计算机"
tags:
  - "运维"
---

以tengine为例，记录添加yum自用打包过程.

<!--more-->

首先,下载tengine

```bash
wget https://github.com/alibaba/tengine/archive/tengine-2.2.2.tar.gz
tar xzvf tengine-2.2.2.tar.gz
cd tengine-tengine-2.2.2/
```

然后安装打包工具fpm

```bash
yum -y install ruby rubygems ruby-devel rpm-build
gem sources -a http://ruby.taobao.org/
gem install fpm
```

编译安装到其他文件夹下

```bash
./configure --prefix=/home/maintain/nginx --conf-path=/home/shared/nginx/conf/nginx.conf --pid-path=/home/shared/nginx/logs/nginx.pid --error-log-path=/home/shared/nginx/logs/error.log --with-http_ssl_module --with-http_sub_module --with-http_dav_module --with-http_flv_module --with-http_gzip_static_module --with-http_stub_status_module --with-http_v2_module --with-http_realip_module --add-module=ngx_cache_purge-2.3
make
mkdir /tmp/installdir
make install DESTDIR=/tmp/installdir/

```

打包成rpm包

```text
cd /tmp/installdir/
fpm -s dir -t rpm -n tengine -v 2.2.0 --iteration 1.el6 -C /tmp/installdir/ -p /root

```

打出来的包会在/root文件夹下

然后将rpm安装包上传到自建yum仓库,刷新仓库

```bash
createrepo --update {{ path }}
```

客户端刷新centos yum缓存即可
