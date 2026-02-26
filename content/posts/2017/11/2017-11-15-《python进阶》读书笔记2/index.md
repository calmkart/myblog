---
title: "《Python进阶》读书笔记(2)"
date: 2017-11-15
categories: 
  - "计算机"
  - "读书笔记"
tags: 
  - "python"
---

#### 9.装饰器

既将函数传参给装饰器函数，在函数执行的上下文作某些通用操作。

记得要用@wraps复制函数名称(\_\_name\_\_)，等等属性

使用举例：

```
from functools import wraps

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            #若未登录，返回401
            authenticate()
        return f(*args, **kwargs)
    return decorated
```

<!--more-->

#### 10.可变数据类型和不可变数据类型

可变数据类型：list,dict

不可变数据类型：int,float,string,tuple

可变不可变，指的是变量指向的值：可变，就是说可以改变指向的值而地址不变。不可变，就是说改变变量的值必然改变地址。

python中的赋值(=)，就是左侧得到右侧内存的引用。

举例说明：

```
a = [1]
print a  #---->[1]
b = a
b.append(2)
print a #----->[1,2]
```

因为list为可变数据类型，而a和b指向同一片内存。当对b做+=操作时，只是向后扩充内存内容，而不会修改内存位置。所以a也改变了。

同时要注意，python函数被定义时，默认参数只会被计算一次，不会每次都计算。所以，默认参数最好不要用可变数据类型，就算要用，也要注意在之后不要对其做修改。

#### 11.\_\_slots\_\_

在类的定义中使用\_\_slots\_\_=\["name","age"\]，则只有\_\_slots\_\_这个set中的属性可以被分配内存，不在其中的不可被分配内存。

#### 12.容器collections

1.defaultdict

调用不存在的key时，会用默认的工厂方法作为key默认值.

举例说明：

```
from collections import defaultdic

favourite_colors = defaultdict(list)
for name,color in colors:
    favourite_colors[name].append(color)
    #默认用name这个list作为KEY
```

2.counter计数器

```
from collections import counter
c= counter(...)#为内部元素计数
favs = counter(name for name,color in colors)
#为name计数,以dict返回
```

3.deque双向链表

```
from collections import deque
```

4.namedtuple命名元组

```
from collections import namedtuple

animal = namedtuple('animal', 'name age type')
perry = animal(name="perry", age=31, type="cat")
#可以访问perry.name这样访问属性
print perry.name
#输出perry
#可将命名元组转换为dict，用_asdict()方法
perry._asdict()
```

#### 13.dir()

返回对象所有属性和方法

举例：

```
a = [1,2,3]
print dir(a)
```

#### 14.type()和id()

type()返回对象类型，id()返回不同种类对象唯一ID

#### 15.推导式

1.列表推导式

通过for和if生成list

举例说明：

```
m=[i for i in range(30) if i%3 is 0]
#------------这是list-----这是条件-----
```

语法：

```
variable = [out_exp for out_exp in input_list if out_exp==2]
#----------------------------------这是list------这是条件----
```

2.字典推导式

```
dict = {v:k for k,v in some_dict.items()}
```

 

[《Python进阶》读书笔记(1)](http://www.calmkart.com/?p=124) [《Python进阶》读书笔记(3)](http://www.calmkart.com/?p=150)
