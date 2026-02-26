---
title: "goreplay实现流量复制的AB测试"
date: 2019-05-09
categories: 
  - "计算机"
tags: 
  - "ab测试"
  - "流量复制"
---

AB测试的流量复制工具以前有tcpdump啥的，讲道理不好用，啰里八嗦的，不高明，懂得都懂。所以用一款好用的新货，goreplay。[![](images/0E969B1EE4076B3AE46A718E8EC14C48.jpg)](http://www.calmkart.com/wp-content/uploads/2019/05/0E969B1EE4076B3AE46A718E8EC14C48.jpg)

<!--more-->

github地址:

[https://github.com/buger/goreplay](https://github.com/buger/goreplay)

先下载二进制文件到机器上，使用方法及其简单

```
#假设有两台机器,机器名是vm1和vm2,需要将vm1的8900上的请求流量复制到vm2的8900上,并且限制为get请求,然后将流量缩小为原来的10%，并将vm2的8900上收到的请求和返回输出到文件里，如下操作即可

#vm1
./gor --input-raw :8900 --output-http="http://vm2:8900|10%" --http-allow-method GET

#vm2
./gor --input-raw :8900 --output-http-track-response --input-raw-track-response --output-file=goreplay_response.log

```

以上流程是用goreplay将vm1中8900端口上的请求流量捕获，筛选出GET请求，缩小到10%流量转发给vm2 然后再vm2上用goreplay将vm2中8900端口上的请求流量和返回流量捕获，输出进文件goreplay\_response.log中

从而实现AB测试

操作流程非常简单轻松，还有更多详细的配置参数配置项，有需要可以查查文档，随手记录下。

---

## 历史评论 (3 条)

*以下评论来自原 WordPress 站点，仅作存档展示。*

> **kulumer** (2019-05-10 14:27)
>
> 您好，我们组最近在调研流量回放的框架，请问您有没有推荐的在用在生产环境的呢

  > ↳ **calmkart** (2019-05-11 15:16)
  >
  > 推荐两种方式
  > 1.nginx+mirror module
  > 这种方式通过nginx做流量镜像
  > 2.goreplay

    > ↳ **kulumer** (2019-05-15 12:09)
    >
    > 谢谢您，刚部署试用了goreplay, 用来做流量回放效果确实不错 ，👍
