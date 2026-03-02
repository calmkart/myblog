---
title: "一个关于z-index的小问题"
date: 2018-12-26
description: "最近一直在忙,没空写blog.刚好今天写前端的时候碰到一个挺有意思的问题,记录一下. 问题描述:在bootstrap的modal框里popover没反应."
categories: 
  - "计算机"
---

最近一直在忙,没空写blog.刚好今天写前端的时候碰到一个挺有意思的问题,记录一下.

问题描述:在bootstrap的modal框里popover没反应. <!--more--> 剧情是这样的,要弄一个timeline一样的动态step图,找了一圈除了很多wizard插件之外只有一个ystep可用.打算把ystep的流程图放在boostrap模态框里,放进去初始化ystep之后,发现基本css没问题,就是popover弹出框失效了(起码是视觉上失效了). 第一反应,是不是popover没初始化,马上加上

```text
$("[data-toggle='popover']").popover();
```

没任何作用。

然后在浏览器中调试,发现选择$("\[data-toggle='popover'\]")都是没问题的,查了focus事件,也是有绑定的.

很奇怪,怀疑是不是ystep插件有啥问题,于是把div从模态框里弄了出来,发现popover弹窗恢复正常.

这时候开始想到是不是z-index的层覆盖出了问题,因为之前用bootbox插件生成各种modal的时候总和手写的modal有层叠冲突,果断强加css(bootstap默认的modal z-index大概是2050左右)

```html
<style>
.popover {
z-index: 2099;
}
</style>
```

瞬间管用了,问题解决.
