---
title: "使用kubectl-debug来调试pod"
date: 2019-10-21
categories: 
  - "计算机"
tags: 
  - "golang"
  - "k8s"
  - "kubectl-debug"
  - "kubernetes"
  - "sidecar"
  - "云原生"
  - "容器"
  - "调试"
---

在k8s环境中,我们经常会碰到各种疑难杂症.比如下面这个例子: 某pod无法启动,查看日志显示原来是init时容器无法拉取某个外部网络上的包.我们exec登陆容器后试图调试下产生这个问题的原因,我们输入ping xxx.xxx.xxx,但sh直接提示"找不到ping命令",甚至直接无法exec到一个没有sh的容器中. 这样的情况我们该怎么办呢？这里有一个解决类似问题的调试工具[kubectl-debug](https://github.com/aylei/kubectl-debug) <!--more--> kubectl-debug的原理也很简单,因为docker容器是基于namespace做的隔离,所以可以创建一个新的预装好了各种调试工具的容器,直接加入待调试容器的namespace中,这样就可以与待调试pod共享各类栈,实现方便调试.(有点类似于k8s中的sidecar设计模式,但是使用的是一个用后既销的独立容器)

这里介绍一下简单的使用方式 我们可以直接下载编译好的二进制文件包 [https://github.com/aylei/kubectl-debug/releases](https://github.com/aylei/kubectl-debug/releases) 也可以clone源代码自己做编译(可以获得更多最新修复和更新)

```
# 这里要开启docker,因为是通过docker编译的
git clone https://github.com/aylei/kubectl-debug.git
cd kubectl-debug
make

```

最简单的使用方式

```
kubectl-debug POD_NAME

```

kubectl-debug将拉取nicolaka/netshoot镜像作为默认的debug镜像. 过一小会拉取镜像的功夫,我们创建好了一个插入待调试pod namespace中的调试容器,并且已经获取了stdin和stdout,我们就可以进行调试了. 调试完成后exit退出,kubectl-debug将完成相关的清理工作.

当然,如果觉得默认的nicolaka/netshoot调试镜像不好用,也可以使用自己的私有镜像进行调试

```
# 使用私有仓库镜像,并设置私有仓库使用的kubernetes secret
# secret data原文请设置为 {Username: , Password: }
# 默认secret_name为kubectl-debug-registry-secret,默认namspace为default
kubectl-debug POD_NAME --image calmkart/netshoot:latest --registry-secret-name  --registry-secret-namespace 

```

甚至如果原pod已经无法启动了,我们可以使用fork模式fork出一个新的待调试pod用于调试(自动替换掉entry-point)

```
kubectl debug POD_NAME --fork

```

更多功能可以参考[kubectl-debug官方文档](https://github.com/aylei/kubectl-debug/blob/master/docs/zh-cn.md)

总之这个工具还是非常实用的,我也参与添加了一些增强功能和bug修复.k8s官方据说也将在未来版本增加[临时容器](https://github.com/kubernetes/enhancements/issues/277)功能以支持调试,虽然不知道啥时候能用上,但还是期待的.

---

## 历史评论 (2 条)

*以下评论来自原 WordPress 站点，仅作存档展示。*

> **myway** (2019-10-23 16:59)
>
> 请问下如何调试生产环境的k8s呢，用kubectl-debug会不会有什么风险？

  > ↳ **calmkart** (2019-10-24 20:12)
  >
  > 你只要不乱搞，看不出有啥风险。
  > 乱搞,ex:
  > 1.乱给forkpod打label
  > 2.在debug container里一顿神操作
  > 之类.
