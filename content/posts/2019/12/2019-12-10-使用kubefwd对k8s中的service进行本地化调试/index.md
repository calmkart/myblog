---
title: "使用kubefwd对k8s中的service进行本地化调试"
date: 2019-12-10
description: "大家都知道,k8s中的服务(service)是对k8s中的deployment等对象的一个一致访问点.所以service会有一个vip(headless service没有).无论是普通service的vip或者headless..."
categories: 
  - "计算机"
tags: 
  - "k8s"
  - "kubefwd"
  - "kubernetes"
---

大家都知道,k8s中的服务(service)是对k8s中的deployment等对象的一个一致访问点.所以service会有一个vip(headless service没有).无论是普通service的vip或者headless service的pod ip其实都是k8s集群中的内部ip,在集群内访问它是非常容易的.比如有一个service叫nginx,我们在集群内的另一个pod里既可以对这个nginx service的vip进行get访问,也可以通过coredns对这个nginx service的域名如(nginx, nginx.default等)进行访问.但是在集群外呢?这就麻烦了.

常见的集群外访问service的方式大致分为 LoadBalance, NodePort, ExternalIp等方式, 再细致一点也可以通过Ingress在7层做一层分发再外接上述流量接入,甚至你可以直接将api server做proxy. 很显然的，这些方式如果在我们只是需要对服务进行调试或者随便用用的场景都是要么太复杂(Ingress), 要么花钱(LoadBanlence),要么不靠谱(NodePort).

这时候你会说,嗷,我们可以使用kubectl port-forward 功能,将service的端口port-forward到本地端口.对，没错，这确实是一个不错的解决方式，但这仍然存在非常多的问题。

比如,我们并不想要将nginx service的80端口port-forward到我的8080端口上，就想用80端口，那么如果有两个service分别叫nginx1和nginx2，这不就没法弄了吗？再比如，如果我们port-forward的svc的pod发生了变动,怎么办？再比如,我们就是想像在集群内一样，通过service的内部域名对其访问(nginx, nginx.default等)，怎么办？再比如，如果我们有100个服务，难道我们要手动对每个服务port-forward然后手动选择一个没用过的端口吗？甚至，当我们的服务创建,删除,我们又得手动操作,这是何等的麻烦？

基于上述问题,一个叫[kubefwd](https://github.com/txn2/kubefwd)的工具出现了。 <!--more-->

我们先从使用开始。 首先有一个集群,有nginx和nginx1两个service,其中nginx是普通service,而nginx1是headless service.

```bash
➜  ~ kubectl get pods
NAME                                 READY   STATUS      RESTARTS   AGE
nginx-deployment-5cdfb5fc49-fgn78    1/1     Running     0          24d
nginx-deployment-5cdfb5fc49-rjg26    1/1     Running     0          24d
nginx-deployment1-75c5577b94-tp7zr   1/1     Running     0          21d
nginx-deployment1-75c5577b94-vcpn5   1/1     Running     0          21d
pi-gw8s7                             0/1     Completed   0          74d
➜  ~ kubectl get service
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1               443/TCP   74d
nginx        ClusterIP   10.101.159.59           80/TCP    33d
nginx1       ClusterIP   None                    80/TCP    21d
➜  ~

```

然后我们下载最新版的kubefwd([release](https://github.com/txn2/kubefwd/releases))在本地运行。

```bash
➜  kubefwd git:(master) sudo kubefwd svc
Password:
INFO[11:44:47]  _          _           __             _
INFO[11:44:47] | | ___   _| |__   ___ / _|_      ____| |
INFO[11:44:47] | |/ / | | | '_ \ / _ \ |_\ \ /\ / / _  |
INFO[11:44:47] |   <| |_| | |_) |  __/  _|\ V  V / (_| |
INFO[11:44:47] |_|\_\\__,_|_.__/ \___|_|   \_/\_/ \__,_|
INFO[11:44:47]
INFO[11:44:47] Version 0.0.0
INFO[11:44:47] https://github.com/txn2/kubefwd
INFO[11:44:47]
INFO[11:44:47] Press [Ctrl-C] to stop forwarding.
INFO[11:44:47] 'cat /etc/hosts' to see all host entries.
INFO[11:44:47] Loaded hosts file /etc/hosts
INFO[11:44:47] Hostfile management: Original hosts backup already exists at /Users/calmkart/hosts.original
WARN[11:44:47] WARNING: No Pod selector for service kubernetes in default on cluster .
INFO[11:44:47] Forwarding: nginx1:80 to pod nginx-deployment1-75c5577b94-tp7zr:80
INFO[11:44:47] Forwarding: nginx-deployment1-75c5577b94-tp7zr.nginx1:80 to pod nginx-deployment1-75c5577b94-tp7zr:80
INFO[11:44:47] Forwarding: nginx-deployment1-75c5577b94-vcpn5.nginx1:80 to pod nginx-deployment1-75c5577b94-vcpn5:80
INFO[11:44:47] Forwarding: nginx:80 to pod nginx-deployment-5cdfb5fc49-fgn78:80

```

我们可以通过控制台INFO输出清晰的看到,我们已经将普通service nginx port-forward到了它的第一个pod nginx-deployment-5cdfb5fc49-fgn78上，将headless service nginx1 port-forward到了它的第一个pod上，同时还port-forward到了它的每一个pod上(因为headless service中的pod是不等价的).

接着我们查看一下本机的hosts

```bash
➜  ~ cat /etc/hosts
##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1        localhost
127.1.27.1       nginx1 nginx1.default.svc.cluster.local nginx1.default
127.1.27.2       nginx-deployment1-75c5577b94-tp7zr.nginx1 nginx-deployment1-75c5577b94-tp7zr.nginx1.default.svc.cluster.local nginx-deployment1-75c5577b94-tp7zr.nginx1.default
127.1.27.3       nginx-deployment1-75c5577b94-vcpn5.nginx1 nginx-deployment1-75c5577b94-vcpn5.nginx1.default.svc.cluster.local nginx-deployment1-75c5577b94-vcpn5.nginx1.default
127.1.27.4       nginx nginx.default.svc.cluster.local nginx.default

```

厉害了，居然多出了这么多记录。 从这个hosts看起来，我们访问nginx1/nginx1.default.svc.cluster.local/nginx1.default应该都可以访问到k8s集群中的nginx1服务; 我们访问nginx/nginx.default.svc.cluster.local/nginx.default应该都可以访问到k8s集群中的nginx服务,我们来尝试一下。 使用httpie试试

```bash
➜  ~ http get nginx1
HTTP/1.1 200 OK
Accept-Ranges: bytes
Connection: keep-alive
Content-Length: 612
Content-Type: text/html
Date: Tue, 10 Dec 2019 03:57:05 GMT
ETag: "58e66cf5-264"
Last-Modified: Thu, 06 Apr 2017 16:29:41 GMT
Server: nginx/1.11.13

➜  ~ http get nginx
HTTP/1.1 200 OK
Accept-Ranges: bytes
Connection: keep-alive
Content-Length: 612
Content-Type: text/html
Date: Tue, 10 Dec 2019 03:57:17 GMT
ETag: "54999765-264"
Last-Modified: Tue, 23 Dec 2014 16:25:09 GMT
Server: nginx/1.7.9

```

厉害了也，真的管用。

我们尝试在k8s集群中新添加一个service叫nginx2,这个服务和nginx1一样是一个headless service

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment2
  labels:
    app: nginx2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx2
  template:
    metadata:
      labels:
        app: nginx2
        test: test
        test1: test1
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        readinessProbe:
          tcpSocket:
            port: 80
        livenessProbe:
          tcpSocket:
            port: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx2
spec:
  clusterIP: None
  selector:
    app: nginx2
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80

```

 

```bash
➜  ~ kubectl apply -f nginx2.yaml
deployment.apps/nginx-deployment2 created
service/nginx2 created

```

这个时候我们发现运行的kubefwd INFO记录显示了如下内容

```bash
INFO[12:01:12] Forwarding: nginx2:80 to pod nginx-deployment2-5995ddf44f-6r9fg:80
INFO[12:01:12] Forwarding: nginx-deployment2-5995ddf44f-6r9fg.nginx2:80 to pod nginx-deployment2-5995ddf44f-6r9fg:80
INFO[12:01:12] Forwarding: nginx-deployment2-5995ddf44f-d5q9d.nginx2:80 to pod nginx-deployment2-5995ddf44f-d5q9d:80

```

我们来看看Hosts

```bash
127.1.27.5       nginx2 nginx2.default.svc.cluster.local nginx2.default
127.1.27.6       nginx-deployment2-5995ddf44f-6r9fg.nginx2 nginx-deployment2-5995ddf44f-6r9fg.nginx2.default.svc.cluster.local nginx-deployment2-5995ddf44f-6r9fg.nginx2.default
127.1.27.7       nginx-deployment2-5995ddf44f-d5q9d.nginx2 nginx-deployment2-5995ddf44f-d5q9d.nginx2.default.svc.cluster.local nginx-deployment2-5995ddf44f-d5q9d.nginx2.default

```

果然，新添加了这些记录。看来我们通过本地域名解析nginx2就可以访问到nginx2服务啦.我们来试试.

```bash
➜  ~ http get nginx2
HTTP/1.1 200 OK
Accept-Ranges: bytes
Connection: keep-alive
Content-Length: 612
Content-Type: text/html
Date: Tue, 10 Dec 2019 04:03:23 GMT
ETag: "5dd3e500-264"
Last-Modified: Tue, 19 Nov 2019 12:50:08 GMT
Server: nginx/1.17.6

```

果然，和我们预想的一样。 最后我们通过ctrl+c停止kubefwd.

```bash
^CWARN[12:04:08] Stopped forwarding nginx-deployment1-75c5577b94-vcpn5.nginx1 in default.
WARN[12:04:08] Stopped forwarding nginx-deployment2-5995ddf44f-d5q9d.nginx2 in default.
WARN[12:04:08] Stopped forwarding nginx2 in default.
WARN[12:04:08] Stopped forwarding nginx in default.
WARN[12:04:08] Stopped forwarding nginx-deployment2-5995ddf44f-6r9fg.nginx2 in default.
WARN[12:04:08] Stopped forwarding nginx1 in default.
WARN[12:04:08] Stopped forwarding nginx-deployment1-75c5577b94-tp7zr.nginx1 in default.
INFO[12:04:08] Done...

```

terminal中显示我们停止了nginx,nginx1,nginx2的转发,我们再来看看hosts呢？

```bash
##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1        localhost

```

果然，已经清理完毕了。

以上基本就是常规使用的全过程，接下来大致讲讲原理吧。

kubefwd项目过去的运行机制是在运行时通过api-server拉取k8s中的所有service服务信息(List),并将服务分为普通服务和无头服务两类,通过普通服务的第一个pod/无头服务的每一个pod的port-forward subresource对其做转发,并在本地为其创建无人使用的环回接口ip,将其转发上去,实现端口的隔离。

后来代码经过我的一次很大的重构,目前的流程是像一个自定义控制器一样,在启动时ListAndWatch api-server的service信息，能够自动感知api-server的服务变化，当服务被创建/删除，服务转发的pod被修改/删除时开启对应的goroutine对其进行port-forward并修改Hosts(过程中加锁).当kubefwd被停止时(或者某service被删除时)启动清理流程，结束转发并清理hosts.

其实原理上并不复杂，但确实是能在k8s环境中解决某一个方向上的问题的。 欢迎大家来试着使用使用。

<div class="archived-comments">

<h2>历史评论 (1 条)</h2>
<p class="comment-notice">以下评论来自原 WordPress 站点，仅作存档展示。</p>
<div class="comment-item">
<div class="comment-meta"><strong>1</strong> (2019-12-16 17:03)</div>
<div class="comment-body">1</div>
</div>
</div>
