---
title: "用phpMyAdmin在线管理mysql数据库"
date: 2017-11-20
description: "本站phpMyAdmin测试地址： www.calmkart.com/phpMyAdmin"
categories: 
  - "计算机"
tags: 
  - "mysql"
  - "phpmyadmin"
---

本站phpMyAdmin测试地址：

[www.calmkart.com/phpMyAdmin](http://www.calmkart.com/phpMyAdmin) <!--more-->

1.在[phpMyAdmin](https://www.phpmyadmin.net/)官方网站下载最新版本软件

2.unzip解压，文件夹改名为phpMyAdmin

3.把config.sample.inc.php复制一份为config.inc.php

4.修改以下两处

```sql
$cfg[‘Servers’][$i][‘controluser’] = ‘您的数据库名称’;
$cfg[‘Servers’][$i][‘controlpass’] = ‘您的数据库密码’;
```

**注意：**

**root用户要用sudo所以无权限登陆，这时候推荐专门设置一个phpmyadmin用户用于管理**

```sql
mysql -uroot -p
CREATE USER 'phpmyadmin'@'localhost' IDENTIFIED BY 'some_pass';
GRANT ALL PRIVILEGES ON *.* TO 'phpmyadmin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

5.把phpMyAdmin文件夹复制到nginx配置的server主目录，我这里是/var/www/html/

6.访问http://域名/phpMyAdmin即可
