---
title: "增强nginx的autoindex功能(文件排序，文件MD5值)"
date: 2017-12-18
categories: 
  - "计算机"
tags: 
  - "nginx"
---

原始的nginx文件服务器autoindex功能非常单一，也不够美观，连按时间或者文件大小排序功能都没有，所以通过nginx插件和修改源码的方式为其增加了一些新的功能。 最终效果如下：

![](images/zzxg-1.jpg) <!--more--> 用到的插件为file-md5和ngx-fancyindex，nginx版本是1.6.2

```
git clone https://github.com/cfsego/file-md5.git
git clone https://github.com/aperezdc/ngx-fancyindex.git
wget https://github.com/nginx/nginx/archive/release-1.6.2.tar.gz
```

修改/ngx-fancyindex/template.h文件

```
//插入script
"<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js\">"
"</script>"
"<script src=\"/static/md5.js\">"
"</script>"
//修改页面表格宽度
"<tr>"
"<th style=\"width:30%\"><a href=\"?C=N&O=A\">File Name</a>&nbsp;<a href=\"?C=N&O=D\">&nbsp;&darr;&nbsp;</a></th>"
"<th style=\"width:35%\"><a href=\"?C=S&O=A\">File Size</a>&nbsp;<a href=\"?C=S&O=D\">&nbsp;&darr;&nbsp;</a></th>"
"<th style=\"width:25%\"><a href=\"?C=M&O=A\">Date</a>&nbsp;<a href=\"?C=M&O=D\">&nbsp;&darr;&nbsp;</a></th>"
"</tr>"
```

接着执行

```
cd ./nginx-release-1.6.2
./auto/configure --prefix=/usr/local/nginx --with-pcre --with-http_stub_status_module --with-http_ssl_module --with-http_gzip_static_module --add-module=../file-md5-master --add-module=../ngx-fancyindex
make
```

然后修改nginx配置文件

```
vi /etc/nginx/site-enable/default
###########################
更多fancyindex插件配置选项参考
http://www.ttlsa.com/nginx/nginx-module-ngx-fancyindex/
https://www.nginx.com/resources/wiki/modules/fancy_index/#directives
###########################
root /var/www; //改为需要路径，测试机中是/var/www/
location / {
 36         # First attempt to serve request as file, then
 37         # as directory, then fall back to displaying a 404.
 38         fancyindex on;
 39         fancyindex_exact_size off;
 40         fancyindex_ignore "static";
 41         add_header Content-MD5 $file_md5;
 42     }
```

在需要分享的路径创建文件./static/md5.js，测试机中是/var/www/

```
mkdir /var/www/static
vi /var/www/static/md5.js

```

```
$(document).ready(function(){
	var current_index = 1;
	function get_md5(){
		if(current_index==$("tr").length){
			return;
		}

		var url = $("tr")[current_index].childNodes[0].childNodes[0].href;
		$.ajax({
        	url: url,           
        	type: "HEAD",
        	complete: function(jqXHR, textStatus) {
        		var file_size = $("tr")[current_index].childNodes[1].childNodes[0].data;     
        		var md5 = jqXHR.getResponseHeader("Content-MD5");
        		console.log(jqXHR.getAllResponseHeaders());
        		if(md5!=null && file_size!="-"){
        			$("tr")[current_index].childNodes[1].innerHTML += ("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp"+"[md5:"+md5+"]");
        			}
        		current_index++;
        		get_md5();
        		}
    		});
		}
	get_md5();
});

```

然后在nginx-release-1.6.2目录下

```
killall nginx
cd ./objs
./nginx -c /etc/nginx/nginx.conf

```

即可

#### **关于md5.js原理的一些小说明：**

file-md5模块是第三方模块，必须通过手动编译安装。 功能是将文件md5值插入文件的http头的Content-MD5字段中，效果如图

![](images/2.jpg)

在ngx-fancyindex源码中，调用md5.js的js脚本，从前端通过jquery ajax读取所有文件http头重的Content-MD5字段，再写入页面中。

因为ajax是异步的，所以无法通过普通的for循环或者赋值给全局变量的方式运行，所以要用递归+回调函数的方式，才能达成正确的效果。

设置递归终止条件current\_index==$("tr").length，循环遍历所有的文件连接，提取http头中的md5值写入页面中即可。

但性能还是有些问题的，有些大文件的计算比较浪费时间。这里已经将ajax的请求type换成了HEAD类型，因为不再请求文件主体，所以请求速度是GET类型的10倍以上。

所有文件git地址： [https://github.com/calmkart/nginx\_autoindex-](https://github.com/calmkart/nginx_autoindex-) 编译好的nginx可执行文件： [https://github.com/calmkart/nginx\_autoindex-/archive/0.1.tar.gz](https://github.com/calmkart/nginx_autoindex-/archive/0.1.tar.gz)
