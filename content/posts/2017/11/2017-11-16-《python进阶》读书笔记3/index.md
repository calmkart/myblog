---
title: "《Python进阶》读书笔记(3)"
date: 2017-11-16
categories: 
  - "计算机"
  - "读书笔记"
tags: 
  - "python"
---

#### 16.异常处理

捕获所有异常：

```
except Exception as e:
    print e
```

<!--more--> try/except/finally语句:

```
try:
    #首先执行
    pass
except:
    #异常的话执行
    pass
finally:
    #无论是否异常，在最后都执行
    pass
```

try/else语句：

```
try:
    #首先执行
    pass
else:
    #异常的话执行,且不被捕获异常
    pass
finally:
    #无论是否异常，在最后都执行
    pass
```

#### 17.简易webserver

python2:

```
python -m SimpleHTTPServer 8888
#在当前文件夹建立简易http服务器，端口为8888
```

python3:

```
python -m http.server 8888
#在当前文件夹建立简易http服务器，端口为8888
```

注意，在python2中SimpleHTTPServer是处理GET和HEAD请求的，而CGIHTTPServer处理POST请求。

#### 18.pprint

可以用于打印dict等数据结构，比较漂亮

```
from pprint import pprint
    pprint({a:1,b:2})
```

#### 19.for/else从句

else仅在for循环正常结束时才会执行，当for循环被break时，不执行else

举例说明：

```
for item in container:
    if search_something(item):
        # Found it!
        process(item)
        break
else:
    # Didn't find anything..
    not_found_in_container()
```

#### 20.用with块自动释放句柄

with块可在有异常时，自动释放句柄

```
with open('a.txt','r+') as f:
#打开成功才会获得句柄，有异常则自动释放
    file = f.read()
```

用io.open可制定编码方式：

```
import io 
with io.open('a.txt', 'w', encoding='utf-8') as f:
    f.write(.......)
```

而直接使用open(),do,close()的方式，可能因为各种error而导致没有释放资源。

#### 21.协程

与生成器有点像，但生成器是返回可迭代对象的生产者，而携程是接受参数的消费者。

```
def grep(pattern):
    print("Searching for", pattern)
    while True:
        line = (yield)
        if pattern in line:
            print(line)
```

我们通过send方法传送给协程数据，然后用close()方法来关闭

```
search = grep('coroutine')
next(search)
#output: Searching for coroutine
search.send("I love you")
search.send("Don't you love me?")
search.send("I love coroutine instead!")
#output: I love coroutine instead!
search = grep('coroutine')
search.close()
```

 

[《Python进阶》读书笔记(1)](http://www.calmkart.com/?p=124) [《Python进阶》读书笔记(2)](http://www.calmkart.com/?p=139)
