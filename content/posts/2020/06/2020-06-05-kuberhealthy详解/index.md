---
title: "kuberhealthy详解"
date: 2020-06-05
---

## 是什么

官方的介绍中是这样说的

> An operator for synthetic monitoring on Kubernetes

_`一个用于合成监控的operator`_

也就是一个用于在k8s集群中运行各种健康检查并上报集群巡检状态的operator

## 流程逻辑

大致运行流程图如下所示

![gif](images/kh-ds-check.gif) <!--more-->

kuberhealthy将创建两个crd，分别为

- khchecks
- khstates

其中 `khchecks` cr用来描述我们需要在集群中创建并持续运行的巡检详情

而`khstate` cr用来记录每一个巡检的当前巡检结果

kuberhealthy operator运行在集群中，会实时监听`khchecks` custom resource的变化。当我们创建一个`khcheck` cr时，kuberhealthy会根据cr中的各种描述字段创建对应的巡检checked pod， checked pod执行巡检逻辑，并将结果返回给kuberhealthy deployment pod。

kuberhealthy支持多种巡检结果输出，如`khstate` cr对象就是用来保存某khcheck巡检当前结果的。同时也支持json/prometheus等多种结果输出。

## 简单使用

1. 部署 kuberhealthy
    
    ```bash
    git clone https://github.com/Comcast/kuberhealthy.git
    cd kuberhealthy
    kubectl apply -f deploy/kuberhealthy.yaml
    ```
    

我们将创建一个replicas为2的kuberhealthy deployment。(实际工作的只有一个pod，另一个为保证高可用，kuberhealthy会进行选主操作，但过程实际上有bug)

同时kuberhealthy还将为我们创建一堆khcheck巡检全家桶(其实很多都是我们不需要的)，我们可以通过

```
kubectl get khchecks -n kuberhealthy
```

进行查询，不需要的可以删除

2. 部署一个简单的巡检khcheck

http-check为官方提供的若干巡检用例之一，主要功能是向一个指定的url发送get请求，成功则巡检成功，失败则巡检失败.

样例yaml如下

```yaml
---
apiVersion: comcast.github.io/v1
kind: KuberhealthyCheck # cr类型为kuberhealthyCheck
metadata:
  name: http
  namespace: kuberhealthy
spec:
  runInterval: 2m # 巡检周期
  timeout: 6m # 巡检超时时间
  podSpec:
    containers:
    - name: http
      image: kuberhealthy/http-check:v1.1.1 # 这里为实现巡检逻辑的镜像
      imagePullPolicy: IfNotPresent
      env:
        - name: CHECK_URL # 我们通过env注入，控制http-check所发送get请求的url地址，实现同一个巡检镜像但又灵活的巡检
          value: "http://google.com"
      resources:
        requests:
          cpu: 15m
          memory: 15Mi
        limits:
          cpu: 25m
      restartPolicy: Always
    terminationGracePeriodSeconds: 5
```

我们apply之后，会创建一个khcheck对象，同时kuberhealthy deployment pod会根据khcheck cr中的描述，创建出巡检pod。

3. 查看巡检pod状态，查询巡检结果

我们可以直接在kuberhealthy namespace中查看巡检pod状态

```bash
kubectl get pod -n kuberhealthy
```

我们也可以通过查看khstate自定义资源对象查询当前巡检结果

```bash
kubectl get khstate -n kuberhealthy
kubectl get khstate -n kuberhealthy <example> -o yaml
```

我们还可以通过kuberhealthy service/pod提供的http接口查询巡检结果 _访问kuberhealthy service 80端口或 kuberhealthy master pod 8080端口_

```json
{
    "OK": true,
    "Errors": [],
    "CheckDetails": {
        "kuberhealthy/daemonset": {
            "OK": true,
            "Errors": [],
            "RunDuration": "22.512278967s",
            "Namespace": "kuberhealthy",
            "LastRun": "2019-11-14T23:24:16.7718171Z",
            "AuthoritativePod": "kuberhealthy-67bf8c4686-mbl2j",
            "uuid": "9abd3ec0-b82f-44f0-b8a7-fa6709f759cd"
        },
        "kuberhealthy/deployment": {
            "OK": true,
            "Errors": [],
            "RunDuration": "29.142295647s",
            "Namespace": "kuberhealthy",
            "LastRun": "2019-11-14T23:26:40.7444659Z",
            "AuthoritativePod": "kuberhealthy-67bf8c4686-mbl2j",
            "uuid": "5f0d2765-60c9-47e8-b2c9-8bc6e61727b2"
        },
        "kuberhealthy/dns-status-internal": {
            "OK": true,
            "Errors": [],
            "RunDuration": "2.43940936s",
            "Namespace": "kuberhealthy",
            "LastRun": "2019-11-14T23:34:04.8927434Z",
            "AuthoritativePod": "kuberhealthy-67bf8c4686-mbl2j",
            "uuid": "c85f95cb-87e2-4ff5-b513-e02b3d25973a"
        },
        "kuberhealthy/pod-restarts": {
            "OK": true,
            "Errors": [],
            "RunDuration": "2.979083775s",
            "Namespace": "kuberhealthy",
            "LastRun": "2019-11-14T23:34:06.1938491Z",
            "AuthoritativePod": "kuberhealthy-67bf8c4686-mbl2j",
            "uuid": "a718b969-421c-47a8-a379-106d234ad9d8"
        }
    },
    "CurrentMaster": "kuberhealthy-7cf79bdc86-m78qr"
}
```

## 编写自定义巡检

我们以http-check为例，说明如何编写一个自定义巡检

首先我们来查看一下http-check的main.go核心代码

```go
package main

import (
    "fmt"
    "net/http"
    "os"
    "strconv"
    "strings"

    kh "github.com/Comcast/kuberhealthy/v2/pkg/checks/external/checkclient"
    log "github.com/sirupsen/logrus"
)

var (
    // HTTP endpoint to send a request to.
    checkURL = os.Getenv("CHECK_URL")
)

func init() {
    // Check that the URL environment variable is valid.
    if len(checkURL) == 0 {
        log.Fatalln("Empty URL. Please update your CHECK_URL environment variable.")
    }

    // If the URL does not begin with HTTP, exit.
    if !strings.HasPrefix(checkURL, "http") {
        log.Fatalln("Given URL does not declare a supported protocol. (http | https)")
    }
}

func main() {
    log.Infoln("Beginning check.")

    // Make a GET request.
    r, err := http.Get(checkURL)
    if err != nil {
        reportErr := fmt.Errorf("error occurred performing a " + http.MethodGet + " to " + checkURL + ": " + err.Error())
        log.Errorln(reportErr.Error())
        reportFailureErr := kh.ReportFailure([]string{reportErr.Error()})
        if reportFailureErr != nil {
            log.Fatalln("error when reporting to kuberhealthy:", reportFailureErr.Error())
        }
        os.Exit(0)
    }

    // Check if the response status code is a 200.
    if r.StatusCode == http.StatusOK {
        log.Infoln("Got a", r.StatusCode, "with a", http.MethodGet, "to", checkURL)
        reportSuccessErr := kh.ReportSuccess()
        if err != nil {
            log.Fatalln("error when reporting to kuberhealthy:", reportSuccessErr.Error())
        }
        os.Exit(0)
    }

    reportErr := fmt.Errorf("unable to retrieve a " + strconv.Itoa(http.StatusOK) + " from " + checkURL + " got a " + strconv.Itoa(r.StatusCode) + " instead")
    log.Errorln(reportErr.Error())
    reportFailureErr := kh.ReportFailure([]string{reportErr.Error()})
    if reportFailureErr != nil {
        log.Fatalln("error when reporting to kuberhealthy:", reportFailureErr.Error())
    }

    os.Exit(0)
}
```

其实其中除了巡检逻辑，和kuberhealthy相关的方法只有两个

```go
// 导入kuberhealthy自定义巡检client库
import  kh "github.com/Comcast/kuberhealthy/v2/pkg/checks/external/checkclient"

// 如果巡检成功，调用ReportSuccess方法上报成功
kh.ReportSuccess()

// 如果巡检失败，调用ReportFailure方法上报失败
kh.ReportFailure([]string{})
```

然后将其build成一个镜像

_Dockerfile_

```Dockerfile

FROM golang:1.13 AS builder
WORKDIR /build
COPY go.mod go.sum /build/
RUN go mod download

COPY . /build
WORKDIR /build/cmd/http-check
ENV CGO_ENABLED=0
RUN go build -v
RUN groupadd -g 999 user && \
    useradd -r -u 999 -g user user
FROM scratch
COPY --from=builder /etc/passwd /etc/passwd
USER user
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /build/cmd/http-check/http-check /app/http-check
ENTRYPOINT ["/app/http-check"]
```

_Makefile_

```Makefile
build:
    docker build -t kuberhealthy/http-check:v1.2.2 -f Dockerfile ../../

push:
    docker push kuberhealthy/http-check:v1.2.2
```

这样就完成了一个自定义巡检用例的全部编写和打包

#### 使用非go语言怎么办？

如果使用的是非golang编写巡检用例，无法调用官方外部巡检client库，也是很简单的。

1. 读取`KH_REPORTING_URL`环境变量
2. 将如下`JSON巡检结果`通过`POST方法`发送到`KH_REPORTING_URL`地址上
    
    ```yaml
    {
    "Errors": [
    "Error 1 here",
    "Error 2 here"
    ],
    "OK": false
    }
    ```
    

## kuberhealthy代码详解

### 首先概览一下kuberhealthy的代码组织结构

_不重要的目录和文件已省略_

```
./
├── clients # 这里存放其他语言编写自定义巡检的client库(目前只有js)
├── cmd # 存放若干巡检用例代码，其中kuberhealthy子目录为核心代码主目录
│   ├── kuberhealthy # kuberhealthy代码主目录
│   │   ├── Dockerfile
│   │   ├── Makefile
│   │   ├── crd.go
│   │   ├── fakecheck_test.go
│   │   ├── influx.go
│   │   ├── kuberhealthy.go
│   │   ├── kuberhealthyCheck.go
│   │   ├── main.go
│   │   ├── main_test.go
│   │   ├── reflector.go
│   │   ├── test
│   │   │   └── basicCheckerPod.yaml
│   │   ├── util.go
│   │   ├── util_test.go
│   │   └── webserver_test.go
├── deploy # 存放一些部署Yaml
├── docs # 存放文档
└── pkg # 存放一些需要使用到的包
    ├── aws
    ├── checks #这里比较核心，存放了大量巡检生命周期逻辑
    │   └── external
    │       ├── checkclient
    │       │   └── main.go
    │       ├── checker_test.go
    │       ├── main.go
    │       ├── main_test.go
    │       ├── status
    │       │   └── main.go
    │       ├── test
    │       │   └── basicCheckerPod.yaml
    │       ├── util
    │       │   └── main.go
    │       └── whitelist_test.go
    ├── health
    ├── khcheckcrd # khcheck cr对象相关定义代码
    ├── khstatecrd # khstate cr对象相关定义代码
    ├── kubeClient
    ├── masterCalculation
    └── metrics
```

其实最核心的只有两个目录

- cmd/kuberhealthy
    - 实现了kuberhealthy deployment master pod中的核心逻辑，包括如何监听khcheck对象的变化，如何周期性的运行巡检用例，如何判断超时，如何写入巡检状态
    - 还包括了influx/prometheus上游的支持，以及http服务器(用于接收巡检结果和提供巡检结果查询)
- pkg/checks
    - 实现了某一个巡检任务的全部逻辑，通过一个interface暴露，包括 运行检查/结束检查/获取当前巡检结果 等若干方法
    - 包括了编写自定义巡检所使用的client库，位于`pkg/checks/external/checkclient`中

### 核心逻辑

核心逻辑从`cmd/kuberhealthy/main.go`开始

```go
func main() {

    // Create a new Kuberhealthy struct
    kuberhealthy = NewKuberhealthy()
    kuberhealthy.ListenAddr = listenAddress

    // create run context and start listening for shutdown interrupts
    khRunCtx, khRunCtxCancelFunc := context.WithCancel(context.Background())
    kuberhealthy.shutdownCtxFunc = khRunCtxCancelFunc // load the KH struct with a func to shutdown its control system
    go listenForInterrupts()

    // tell Kuberhealthy to start all checks and master change monitoring
    kuberhealthy.Start(khRunCtx)

    time.Sleep(time.Second * 90) // give the interrupt handler a period of time to call exit before we shutdown
    <-time.After(terminationGracePeriod + (time.Second * 10))
    log.Errorln("shutdown: main loop was ready for shutdown for too long. exiting.")
    os.Exit(1)
}
```

这里新建了一个Kuberhealthy对象，并调用Start方法。

我们来看看Start方法做了哪些事情

```go
// Start inits Kuberhealthy checks and master monitoring
func (k *Kuberhealthy) Start(ctx context.Context) {

    // start the khState reflector
    go k.stateReflector.Start()

    // if influxdb is enabled, configure it
    if enableInflux {
        k.configureInfluxForwarding()
    }

    // Start the web server and restart it if it crashes
    go kuberhealthy.StartWebServer()

    // find all the external checks from the khcheckcrd resources on the cluster and keep them in sync.
    // use rate limiting to avoid reconfiguration spam
    maxUpdateInterval := time.Second * 10
    externalChecksUpdateChan := make(chan struct{}, 50)
    externalChecksUpdateChanLimited := make(chan struct{}, 50)
    go notifyChanLimiter(maxUpdateInterval, externalChecksUpdateChan, externalChecksUpdateChanLimited)
    go k.monitorExternalChecks(ctx, externalChecksUpdateChan)

    // we use two channels to indicate when we gain or lose master status. use rate limiting to avoid
    // reconfiguration spam
    becameMasterChan := make(chan struct{}, 10)
    lostMasterChan := make(chan struct{}, 10)
    go k.masterMonitor(ctx, becameMasterChan, lostMasterChan)

    // loop and select channels to do appropriate thing when master changes
    for {
        select {
        case <-ctx.Done(): // we are shutting down
            log.Infoln("control: shutting down from context abort...")
            return
        case <-becameMasterChan: // we have become the current master instance and should run checks
            // reset checks and re-add from configuration settings
            log.Infoln("control: Became master. Reconfiguring and starting checks.")
            k.StartChecks()
        case <-lostMasterChan: // we are no longer master
            log.Infoln("control: Lost master. Stopping checks.")
            k.StopChecks()
        case <-externalChecksUpdateChanLimited: // external check change detected
            log.Infoln("control: Witnessed a khcheck resource change...")

            // if we are master, stop, reconfigure our khchecks, and start again with the new configuration
            if isMaster {
                log.Infoln("control: Reloading external check configurations due to khcheck update")
                k.RestartChecks()
            }
        }
    }
}
```

这里的流程大概如下

- 开启khstate的监听
- 开启http server接收巡检pod的返回和暴露巡检结果
- 通过`k.monitorExternalChecks()`监听khcheck cr的变化，并通过externalChecksUpdateChan channel返回
- 通过`notifyChanLimiter()`对监听到khcheck cr变化的消息做限流
- 通过`k.masterMonitor()`进行选择master pod工作实现高可用
- 最后的一个`for-select`循环中，当接收到外部巡检变化channel消息时，重启所有巡检。当本实例成为master时，启动所有巡检，当本实例失去master身份时，停止所有巡检.

### 细节

#### 1\. StartWebServer方法

```go
// StartWebServer starts a JSON status web server at the specified listener.
func (k *Kuberhealthy) StartWebServer() {
    log.Infoln("Configuring web server")
    http.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
        err := k.prometheusMetricsHandler(w, r)
        if err != nil {
            log.Errorln(err)
        }
    })

    // Accept status reports coming from external checker pods
    http.HandleFunc("/externalCheckStatus", func(w http.ResponseWriter, r *http.Request) {
        err := k.externalCheckReportHandler(w, r)
        if err != nil {
            log.Errorln("externalCheckStatus endpoint error:", err)
        }
    })

    // Assign all requests to be handled by the healthCheckHandler function
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        err := k.healthCheckHandler(w, r)
        if err != nil {
            log.Errorln(err)
        }
    })

    // start web server any time it exits
    for {
        log.Infoln("Starting web services on port", k.ListenAddr)
        err := http.ListenAndServe(k.ListenAddr, nil)
        if err != nil {
            log.Errorln("Web server ERROR:", err)
        }
        time.Sleep(time.Second / 2)
    }
}
```

我们可以看到，http server共有三个api

- /metrics
    
    为prometheus暴露监控数据
- /externalCheckStatus
    
    接收巡检pod的巡检结果返回(巡检pod会往这个api里post json数据)
- /
    
    为我们查看当前集群巡检结果提供接口(返回json数据)

#### 2\. monitorExternalChecks方法

```go
// monitorExternalChecks watches for changes to the external check CRDs
func (k *Kuberhealthy) monitorExternalChecks(ctx context.Context, notify chan struct{}) {

    ...
    go k.watchForKHCheckChanges(ctx, c)

    ...
}
```

核心是一个`watchForKHCheckChanges`方法

```go
// watchForKHCheckChanges watches for changes to khcheck objects and returns them through the specified channel
func (k *Kuberhealthy) watchForKHCheckChanges(ctx context.Context, c chan struct{}) {

    log.Debugln("Spawned watcher for KH check changes")

    for {
        log.Debugln("Starting a watch for khcheck object changes")

        // wait a second so we don't retry too quickly on error
        time.Sleep(time.Second)

        // start a watch on khcheck resources
        watcher, err := khCheckClient.Watch(metav1.ListOptions{}, checkCRDResource, listenNamespace)

        if err != nil {
            log.Errorln("error watching khcheck objects:", err)
            continue
        }

        // watch for context expiration and close watcher if it happens
        go func(ctx context.Context, watcher watch.Interface) {
            <-ctx.Done()
            watcher.Stop()
            log.Debugln("khcheck monitor watch stopping due to context cancellation")
        }(ctx, watcher)

        // loop over results and return them to the calling channel until we hit an error, then close and restart
        for khc := range watcher.ResultChan() {
            switch khc.Type {
            case watch.Added:
                log.Debugln("khcheck monitor saw an added event")
                c <- struct{}{}
            case watch.Modified:
                log.Debugln("khcheck monitor saw a modified event")
                c <- struct{}{}
            case watch.Deleted:
                log.Debugln("khcheck monitor saw a deleted event")
                c <- struct{}{}
            case watch.Error:
                log.Debugln("khcheck monitor saw an error event")
                e := khc.Object.(*metav1.Status)
                log.Errorln("Error when watching for khcheck changes:", e.Reason)
                break
            default:
                log.Warningln("khcheck monitor saw an unknown event type and ignored it:", khc.Type)
            }
        }

        // if the context has expired, don't start the watch again. just exit
        watcher.Stop() // TODO - does calling stop twice crash this?  I am assuming not.
        select {
        case <-ctx.Done():
            log.Debugln("khcheck monitor closing due to context cancellation")
            return
        default:
        }
    }
}
```

`watchForKHCheckChanges`将监听khcheck cr的 Added/Modified/Deleted等事件，如果监听到有任何事件，则无差别的通知`monitorExternalChecks`方法中的for循环。在for循环中将List所有khcheck对象，与内存中已保存的`knownSettings`做对比，只要发现有任意变化，就会通过channel通知`Start`方法中的`notifyChanLimiter`方法，如果没有触发`notifyChanLimiter`中的流速限制，就会通知`Start`方法中的for循环,触发以下执行巡检逻辑

```go
    for {
        select {
        ...
        case <-externalChecksUpdateChanLimited: // external check change detected
            log.Infoln("control: Witnessed a khcheck resource change...")

            // if we are master, stop, reconfigure our khchecks, and start again with the new configuration
            if isMaster {
                log.Infoln("control: Reloading external check configurations due to khcheck update")
                k.RestartChecks()
            }
        }
    }
```

#### 3\. RestartChecks方法

当发现有任意khcheck cr变化就会调用`RestartChecks`方法

```go
// RestartChecks does a stop and start on all kuberhealthy checks
func (k *Kuberhealthy) RestartChecks() {
    k.StopChecks()
    k.StartChecks()
}
```

我们发现，kuberhealthy会先停掉所有正在运行的巡检，然后重新开启所有正在运行的巡检。

在`StopChecks`方法中，kuberhealthy会遍历所有存储在内存中的check struct，并分别调用其shutdown()方法，并等待关闭完成

在`StartChecks`方法中，kuberhealthy会先找api-server拉取全部khcheck对象，并生成check struct存于内存中，然后遍历调用runCheck()方法，并等待启动巡检完成

`runCheck()`方法会读取khcheck对象中所保存的周期等信息，启一个goroutine，通过定时器的方式定期调用check struct的Run()方法发起一次检查，并将结果写入checkStates cr中。

_注意，这里的RestartChecks流程是同步逻辑，所以如果在这个流程中因为某些原因卡住，kuberhealthy主流程会直接卡死，只能重启解决。_

#### 4\. external checker的Run方法

kuberhealthy主流程中，`StartChecks()`方法会运行每一个external checker的`Run()`方法

我们打开文件`pkg/checks/external/main.go`中看到checker的`Run()`方法内容如下

```go
// Run executes the checker.  This is ran on each "tick" of
// the RunInterval and is executed by the Kuberhealthy checker
func (ext *Checker) Run(client *kubernetes.Clientset) error {

    // store the client in the checker
    ext.KubeClient = client

    // generate a new UUID for each run
    err := ext.setNewCheckUUID()
    if err != nil {
        return err
    }

    // run a check iteration
    ext.log("Running external check iteration")
    err = ext.RunOnce()

    // if the pod was removed, we skip this run gracefully
    if err != nil && err.Error() == ErrPodRemovedExpectedly.Error() {
        ext.log("pod was removed during check expectedly.  skipping this run")
        return ErrPodRemovedExpectedly
    }

    // if the pod had an error, we set the error
    if err != nil {
        ext.log("Error with running external check:", err)
        return err
    }

    return nil
}
```

我们会发现调用了`RunOnce()`方法，而`RunOnce()`方法非常长，内部逻辑非常复杂，大致流程是先等待当前巡检pod结束，然后运行一个巡检pod，接着等待这个创建出来的pod返回巡检结果。

_这里用了waitgroup等待pod创建和结束完毕，却因为逻辑复杂，wg.Add过多，经常出现卡死的情况_

### 流程图

![流程图](images/流程图.png)

## Kuberhealthy的缺点

总结以下kuberhealthy的缺点主要是以下几点

#### 1\. 监听khcheck的变化但不区分变化类型

这种设计导致了，任何一个khcheck对象发生变化，哪怕是修改，也会让所有巡检全部Shutdown再Start，从而使得khcheck的周期设置形同虚设。(例如：当你修改了a巡检的配置，会发现bcdef巡检都重启并运行了一次)

#### 2\. 同步流程重启全部khchecks有可能导致主流程卡死

因为监听khcheck不区分变化类型的设计，所以带来了所谓的流控策略，专门编写了一个方法用于对变化信号控流，并且主流程的重启全部khchecks是同步流程，如果在重启过程中因为种种原因无法实现shutdown或者run就会主流程卡死，不再响应任何后续指令。出了删pod重建别无他法。

这个问题带来的bug是很多的，并且为了配合这个流程，在khcheck的run流程中使用了极多的信号传递和waitgroup等待，非常容易出问题。我已经修了一些严重的主流程卡死bug但发现只是治标不治本，这种无区分事件监听和全量重启机制不改，这里的主流程卡死bug几乎是不可避免的。无非是触发bug难易程度有差别。

#### 3\. 不支持单次触发型巡检

kuberhealthy在设计上天生就不支持单次触发型巡检，甚至对巡检配置做改动都不应该频繁。

#### 4\. khstate自定义对象设计冗余,巡检历史无记录

kuberhealthy的khstate自定义资源对象用于记录当前巡检结果，但无法查询历史巡检记录。并且khstate这个cr的设计是比较冗余而无意义的，反而平添了很多复杂度。

#### 5\. 废弃的巡检pod/khchecks/khstate/无法得到正确的清理

原生的kuberhealthy创建的巡检pod完成任务后不会被正确删除，所以运行一次检查就会增加一个pod。官方的处理方式是增加一个新cr对象对废弃的巡检pod做cronjob删除。这本身就不是一个非常良好的解决方案。并且khstate其实和khcheck是绑定关系，但并没有采用ownerreferences的方式集联删除，反而在kuberhealhty master pod中启了一个goroutine不停轮询khchecks对象和内存中保存的状态做对比并删除khstate，容易经常性的导致bug。

#### 6\. 高可用选主不稳定

还是因为缺点1中的不区分khcheck对象变化类型重启全部巡检的设计，所以容易导致选主流程中出现主流程卡死的问题。根因在缺点1，基本上改变不了。

#### 7.不支持多集群统一上报

kuberhealthy处理的还是单集群的情况，如果需要多集群统一控制就比较麻烦。也可以通过在client中增加第三方上报的功能，但显得不够优雅。

我曾经试着在不改变设计的前提下对以上一些严重影响使用的问题和bug做修复，经过了几次修复之后发现仅仅是治标不治本。(有兴趣的同学可以关注一下这套同步restart流程，bug多的很。)这些问题的核心还是回到了 不区分变化事件类型 简单粗暴重启全部巡检的设计上。尝试和官方沟通是否能通过改变这个核心设计来重构代码，得到了否定的回答。

其实本质上巡检要实现的功能并不复杂，所以其实与其对kuberhealthy做改动还不如重新实现一个比较简单。

这也是为什么最终我没有采用kuberhealthy为原型的原因，我们的设计参考了kuberhealthy的功能设计，增加了单次触发功能和多集群统一上报功能，解决了废弃的巡检pod的清理问题，增加了巡检历史记录以及监控报警能力，支持白屏化多集群巡检配置部署和巡检结果/巡检pod日志/巡检pod事件查询功能。
