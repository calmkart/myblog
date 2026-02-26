---
title: "配置和使用kube-prometheus"
date: 2019-08-22
categories: 
  - "计算机"
tags: 
  - "alertmanager"
  - "grafana"
  - "k8s"
  - "kubernetes"
  - "prometheus"
  - "云原生"
  - "容器"
  - "监控"
  - "运维"
---

我们在k8s集群中使用云原生的promethues通常需要用到coreos的[prometheus-operater](https://github.com/coreos/prometheus-operator)，它可以方便的帮助我们在k8s中部署和配置使用prometheus。但prometheus并不是开箱即用的，如果要做到开箱即用的监控全家桶，官方提供了两个选择，分别是[prometheus-operater helm chart](https://github.com/helm/charts/tree/master/stable/prometheus-operator)和[kube-prometheus](https://github.com/coreos/kube-prometheus)。这两者都可以为我们提供开箱即用的方式部署promethues+alertmanager+promethues-push-gateway(kube-promethueus不包含,需要单独部署)+grafana全家桶，同时包含[kubernetes-mixin](https://github.com/kubernetes-monitoring/kubernetes-mixin)的一整套报警规则和node-exporter，kube-state-metrics等一系列metrics exporter。区别在于helm chart由社区维护，而kube-promethues由coreos维护。这里我们将以kube-prometheus为例，简要说明配置和使用方式。 <!--more-->

首先是部署，还是非常简单的，我们先将kube-prometheus的仓库clone下来

```
git clone https://github.com/coreos/kube-prometheus.git

```

然后根据官方文档操作即可

```
$ kubectl create -f manifests/

# It can take a few seconds for the above 'create manifests' command to fully create the following resources, so verify the resources are ready before proceeding.
$ until kubectl get customresourcedefinitions servicemonitors.monitoring.coreos.com ; do date; sleep 1; echo ""; done
$ until kubectl get servicemonitors --all-namespaces ; do date; sleep 1; echo ""; done

$ kubectl apply -f manifests/ # This command sometimes may need to be done twice (to workaround a race condition).

```

这里将自动为我们部署prometheus，alertmanager和grafana。我们接下来可以通过port-forward也可以通过ingress将服务暴露出来

```
Prometheus

$ kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090

Then access via http://localhost:9090

Grafana

$ kubectl --namespace monitoring port-forward svc/grafana 3000

Then access via http://localhost:3000 and use the default grafana user:password of admin:admin.

Alert Manager

$ kubectl --namespace monitoring port-forward svc/alertmanager-main 9093

Then access via http://localhost:9093

```

或者编写ingress

```
# ingress-monitor.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: monitoring-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
  namespace: monitoring
spec:
  rules:
  - host: k8s-prometheus.calmkart.com
    http:
      paths:
      - path: /
        backend:
          serviceName: prometheus-k8s
          servicePort: 9090
  - host: k8s-grafana.calmkart.com
    http:
      paths:
      - path: /
        backend:
          serviceName: grafana
          servicePort: 3000
  - host: k8s-alertmanager.calmkart.com
    http:
      paths:
      - path: /
        backend:
          serviceName: alertmanager-main
          servicePort: 9093

# kubectl apply -f ingress-monitor.yaml

```

然后我们就可以访问到prometheus,alertmanager和grafana的服务页面了 [![](images/prometheus.jpg)](http://www.calmkart.com/wp-content/uploads/2019/08/prometheus.jpg)

[![](images/alert-manager.jpg)](http://www.calmkart.com/wp-content/uploads/2019/08/alert-manager.jpg)

[![](images/grafana.jpg)](http://www.calmkart.com/wp-content/uploads/2019/08/grafana.jpg)

这里prometheus已经集成了一些k8s相关的exporter和kubernetes-mixin的报警规则，我们可以从prometheus的status->rules和status->target中查看到。

接下来，我们部署[push-gateway](https://github.com/helm/charts/tree/master/stable/prometheus-pushgateway)

```
#可以参考我这里NodePort的values参数,也可以自行设置
# values.yaml

# Default values for prometheus-pushgateway.
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.
image:
  repository: prom/pushgateway
  tag: v0.9.0
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 9091
  targetPort: 9091

# Optional pod annotations
podAnnotations: {}

# Optional pod labels
podLabels: {}

# Optional service labels
serviceLabels: {}

# Optional serviceAccount labels
serviceAccountLabels: {}

# Optional additional arguments
extraArgs: []

# Optional additional environment variables
extraVars: []

resources: {}
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, uncomment the following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  # limits:
  #   cpu: 200m
  #    memory: 50Mi
  # requests:
  #   cpu: 100m
  #   memory: 30Mi

serviceAccount:
  # Specifies whether a ServiceAccount should be created
  create: true
  # The name of the ServiceAccount to use.
  # If not set and create is true, a name is generated using the fullname template
  name:

## Configure ingress resource that allow you to access the
## pushgateway installation. Set up the URL
## ref: http://kubernetes.io/docs/user-guide/ingress/
##
ingress:
  ## Enable Ingress.
  ##
  enabled: false

    ## Annotations.
    ##
    # annotations:
    #   kubernetes.io/ingress.class: nginx
    #   kubernetes.io/tls-acme: 'true'

    ## Hostnames.
    ## Must be provided if Ingress is enabled.
    ##
    # hosts:
    #   - pushgateway.domain.com

    ## TLS configuration.
    ## Secrets must be manually created in the namespace.
    ##
    # tls:
    #   - secretName: pushgateway-tls
    #     hosts:
    #       - pushgateway.domain.com

tolerations: {}
  # - effect: NoSchedule
  #   operator: Exists

## Node labels for pushgateway pod assignment
## Ref: https://kubernetes.io/docs/user-guide/node-selection/
##
nodeSelector: {}

replicaCount: 1

## Affinity for pod assignment
## Ref: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity
affinity: {}

# Enable this if you're using https://github.com/coreos/prometheus-operator
serviceMonitor:
  enabled: true
  namespace: monitoring
  # fallback to the prometheus default unless specified
  # interval: 10s
  ## Defaults to what's used if you follow CoreOS [Prometheus Install Instructions](https://github.com/helm/charts/tree/master/stable/prometheus-operator#tldr)
  ## [Prometheus Selector Label](https://github.com/helm/charts/tree/master/stable/prometheus-operator#prometheus-operator-1)
  ## [Kube Prometheus Selector Label](https://github.com/helm/charts/tree/master/stable/prometheus-operator#exporters)
  selector:
    prometheus: kube-prometheus
  # Retain the job and instance labels of the metrics pushed to the Pushgateway
  # [Scraping Pushgateway](https://github.com/prometheus/pushgateway#configure-the-pushgateway-as-a-target-to-scrape)
  honorLabels: true

# The values to set in the PodDisruptionBudget spec (minAvailable/maxUnavailable)
# If not set then a PodDisruptionBudget will not be created
podDisruptionBudget:

# helm install --name push-gateway -f values.yaml stable/prometheus-pushgateway

```

然后我们来试着接入内部和外部的prometheus监控target.

1.实现接入内部的target 无论是外部或内部的target都需要一个metrics-server目标，对于内部target而言，一般是一个服务，比如服务calm-server 在prometheus-operater的使用方式中，有一个crd叫serviceMonitor，我们创建一个新的serviceMonitor就创建了一个prometheus的target 我们首先查看monitoring命名空间中已有的serviceMonitor(既prometheus target)

```
[xxx@xxxxx]# kubectl get servicemonitors.monitoring.coreos.com -n monitoring
NAME                      AGE
alertmanager              23d
coredns                   23d
grafana                   23d
ingress-nginx             17d
kube-apiserver            23d
kube-controller-manager   23d
kube-scheduler            23d
kube-state-metrics        23d
kubelet                   23d
node-exporter             23d
prometheus                23d
prometheus-operator       23d
prometheus-pushgateway    19d

```

我们创建一个新的serviceMonitor,将calm-server的/metrics作为target \# calm-server-serviceMonitor.yaml

```
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: calm-server-metrics
  labels:
    k8s-app: calm-server-metrics
  namespace: monitoring
spec:
  namespaceSelector:
    any: true
  selector:
    matchLabels:
      app: calm-server
  endpoints:
  - port: web
    interval: 10s
    honorLabels: true

# kubectl apply -f calm-server-serviceMonitor.yaml

```

这里有几个需要注意的tips:

1.如果service和prometheus不再同一个命名空间，需要设置namespaceSelector，可以单独设置需要搜索的namespace，也可以像上面那样设置为全局搜索。

2.其次，endpoints中设置的port会按照interval设置的时间定时去:/metrics拉取数据，所以对应的服务需要提供相应的metrics(官方有非常多的exporter提供使用，可以参考[https://prometheus.io/docs/instrumenting/exporters/](https://prometheus.io/docs/instrumenting/exporters/))

我们接下来再查看所有serviceMonitor crd api对象，就会发现创建成功，同时prometheus的state->target中也会出现对应的target，我们也可以在prometheus中查询到对应的数据了。

2.实现接入外部target 实现了接入内部的target，那么，k8s集群外部的服务想要接入该怎么办呢？当然还是通过监控k8s集群内service的方式，不是service对应的是一个外部的endpoint对象。下面我们将以calm-server服务为例，说明如何通过k8s的endpoint外部对象接入外部target监控。 首先我们创建一个endpoint对象

```
# calm-server-endpoint.yaml
apiVersion: v1
kind: Endpoints
metadata:
  name: calm-server-metrics
subsets:
  - addresses:
    - ip: x.x.x.x
    ports:
    - name: metrics
      port: xxxx
      protocol: TCP
# kubectl apply -f calm-server-endpoint.yaml

```

我们将ip和port替换成我们的外部服务，apply后就创建了一个endpoint api对象，我们可以通过kubectl get endpoints查看

```
[xxx@xxxxxxx]# kubectl get endpoints
NAME                                  ENDPOINTS                                                           AGE
calm-server-metrics                   10.41.13.17:6789                                                    19d
kubernetes                            10.1.33.159:6443                                                    92d
push-gateway-prometheus-pushgateway   10.240.224.15:9091                                                  19d

```

这里需要注意的是,endpoint对象是不区分namespaces的 接着，我们创建一个service，service的选择器选择calm-server-metrics这个外部endpoint

```
# calm-server-metrics-service.yaml

apiVersion: v1
kind: Service
metadata:
  name: calm-server-metrics
  labels:
    app: calm-server-metrics
spec:
  type: ExternalName
  externalName: x.x.x.x
  clusterIP: ""
  ports:
  - name: metrics
    port: xxxx
    protocol: TCP
    targetPort: 6789

# kubectl apply -f calm-server-metrics-service.yaml

```

我们这个时候访问这个服务，就等于访问了外部的endpoint，既外部服务 我们就可以像上面创建内部服务的serviceMonitor一样，创建serviceMonitor api对象从而更新prometheus target列表了。

接下来我们会有一个问题，如何修改这一系列全家桶的配置呢?比如prometheus的配置，grafana的配置。比如我们需要修改smtp报警配置该怎么办呢？如果是非云原生环境，我们可以直接修改配置文件即可，但在云原生环境中不一样。

kube-prometheus官方文档推荐的方式是使用[jsonnet](https://jsonnet.org/)对官方库做编译修改。那么如何直接通过修改yaml的方式修改配置文件呢？下面将分别介绍如何修改全家桶中的各个配置文件。

1.首先是prometheus的alert rules，我们可以通过修改prometheus-rules.yaml文件修改。 2.其次是alertmanager的config,我们可以修改alertmanager-secret.yaml文件,注意，这是一个secret对象，内容经过了base64加密，我们应该先将内容解密再做修改，修改后再加密替换即可。 3.最后是grafana的配置修改，参考了grafana官方的docker image之后，我们可以先修改grafana-deployment.yaml文件，为其增加一个volume,配置如下

```
apiVersion: apps/v1beta2
kind: Deployment
metadata:
  labels:
    app: grafana
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - image: grafana/grafana:6.2.2
        name: grafana
        ports:
        - containerPort: 3000
          name: http
        readinessProbe:
          httpGet:
            path: /api/health
            port: http
        resources:
          limits:
            cpu: 200m
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 100Mi
        volumeMounts:
        - mountPath: /var/lib/grafana
          name: grafana-storage
          readOnly: false
        - mountPath: /etc/grafana/provisioning/datasources
          name: grafana-datasources
          readOnly: false
        - mountPath: /etc/grafana/provisioning/dashboards
          name: grafana-dashboards
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/apiserver
          name: grafana-dashboard-apiserver
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/controller-manager
          name: grafana-dashboard-controller-manager
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/k8s-cluster-rsrc-use
          name: grafana-dashboard-k8s-cluster-rsrc-use
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/k8s-node-rsrc-use
          name: grafana-dashboard-k8s-node-rsrc-use
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/k8s-resources-cluster
          name: grafana-dashboard-k8s-resources-cluster
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/k8s-resources-namespace
          name: grafana-dashboard-k8s-resources-namespace
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/k8s-resources-pod
          name: grafana-dashboard-k8s-resources-pod
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/k8s-resources-workload
          name: grafana-dashboard-k8s-resources-workload
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/k8s-resources-workloads-namespace
          name: grafana-dashboard-k8s-resources-workloads-namespace
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/kubelet
          name: grafana-dashboard-kubelet
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/nodes
          name: grafana-dashboard-nodes
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/persistentvolumesusage
          name: grafana-dashboard-persistentvolumesusage
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/pods
          name: grafana-dashboard-pods
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/prometheus-remote-write
          name: grafana-dashboard-prometheus-remote-write
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/prometheus
          name: grafana-dashboard-prometheus
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/proxy
          name: grafana-dashboard-proxy
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/scheduler
          name: grafana-dashboard-scheduler
          readOnly: false
        - mountPath: /grafana-dashboard-definitions/0/statefulset
          name: grafana-dashboard-statefulset
          readOnly: false
        - mountPath: /etc/grafana
          name: config-custom
      nodeSelector:
        beta.kubernetes.io/os: linux
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534
      serviceAccountName: grafana
      volumes:
      - emptyDir: {}
        name: grafana-storage
      - name: grafana-datasources
        secret:
          secretName: grafana-datasources
      - configMap:
          name: grafana-dashboards
        name: grafana-dashboards
      - configMap:
          name: grafana-dashboard-apiserver
        name: grafana-dashboard-apiserver
      - configMap:
          name: grafana-dashboard-controller-manager
        name: grafana-dashboard-controller-manager
      - configMap:
          name: grafana-dashboard-k8s-cluster-rsrc-use
        name: grafana-dashboard-k8s-cluster-rsrc-use
      - configMap:
          name: grafana-dashboard-k8s-node-rsrc-use
        name: grafana-dashboard-k8s-node-rsrc-use
      - configMap:
          name: grafana-dashboard-k8s-resources-cluster
        name: grafana-dashboard-k8s-resources-cluster
      - configMap:
          name: grafana-dashboard-k8s-resources-namespace
        name: grafana-dashboard-k8s-resources-namespace
      - configMap:
          name: grafana-dashboard-k8s-resources-pod
        name: grafana-dashboard-k8s-resources-pod
      - configMap:
          name: grafana-dashboard-k8s-resources-workload
        name: grafana-dashboard-k8s-resources-workload
      - configMap:
          name: grafana-dashboard-k8s-resources-workloads-namespace
        name: grafana-dashboard-k8s-resources-workloads-namespace
      - configMap:
          name: grafana-dashboard-kubelet
        name: grafana-dashboard-kubelet
      - configMap:
          name: grafana-dashboard-nodes
        name: grafana-dashboard-nodes
      - configMap:
          name: grafana-dashboard-persistentvolumesusage
        name: grafana-dashboard-persistentvolumesusage
      - configMap:
          name: grafana-dashboard-pods
        name: grafana-dashboard-pods
      - configMap:
          name: grafana-dashboard-prometheus-remote-write
        name: grafana-dashboard-prometheus-remote-write
      - configMap:
          name: grafana-dashboard-prometheus
        name: grafana-dashboard-prometheus
      - configMap:
          name: grafana-dashboard-proxy
        name: grafana-dashboard-proxy
      - configMap:
          name: grafana-dashboard-scheduler
        name: grafana-dashboard-scheduler
      - configMap:
          name: grafana-dashboard-statefulset
        name: grafana-dashboard-statefulset
      - configMap:
          name: grafana-config
        name: config-custom

```

其实就是将一个叫grafana-config的configMap作为volumeMount到/etc/grafana下。 然后我们创建这个configMap

```
# grafana-configmap.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-config
  namespace: monitoring
data:
  grafana.ini: |
    [smtp]
    enabled = true
    host = smtp.calmkart.com:465
    user = calmkart@calmkart.com
    password = xxxxxxxxxx
    skip_verify = false
    from_address = calmkart@calmkart.com
    from_name = grafana

# kubectl apply -f grafana-configmap.yaml

```

这样就可以替换掉默认的配置文件了。

另外还有关于如何为grafana增加plugin等等话题，可以参考官方的相关资料。 就简单介绍到这里吧。

---

## 历史评论 (1 条)

*以下评论来自原 WordPress 站点，仅作存档展示。*

> **曰..曰** (2019-08-26 19:35)
>
> 牛逼的彭董，碾压我等底层劳苦大众，我是服的
