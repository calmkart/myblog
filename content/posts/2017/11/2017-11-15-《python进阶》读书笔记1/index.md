---
title: "《Python进阶》读书笔记(1)"
date: 2017-11-15
categories: 
  - "计算机"
  - "读书笔记"
tags: 
  - "python"
---

#### **1.\*args与\*\*kwargs传参(不定长传参)**

其中\*args是列表传参,\*\*kwargs是字典传参

使用举例：

```
function(fargs, *args, **kwargs)
```

可以用function(1)，function(\[1,2\])，function({a:1})调用函数，都没问题。 <!--more-->

#### **2.生成器yield**

可理解为只能被迭代一次的迭代器，可以节省内存

使用举例：

```
def generation_function():
    for i in range(10):
        yield i

for item in generation_function():
#generation_function是生成器，可被迭代的
    print item
#输出是0->9，但并不需要建立一个list，节省了内存
```

#### **3.匿名函数**

lambda，可减少无需重复函数

格式：lambda 参数:操作

使用举例：

```
lambda x : x+1
```

#### **4.map()**

将function应用于后面参数的所有LIST元素中，返回结果。(python2返回list,python3返回迭代器)

```
map(function, list)
```

也支持多参数:

```
map(function, list1, list2, list3....)
```

常结合lambda匿名函数一起使用

使用举例：

```
items=[1,2,3,4,5]
print map(lambda x : x**2, items)
```

输出\[1,4,9,16,25\]

map的本质既将一个函数映射到若干列表的所有元素上。

#### 5.filter()

过滤list中的元素，返回符合条件元素的list

使用举例：

```
number_list = range(-5,5)
less_than_zero = filter(lambda x : x<0, number_list)
```

输出\[-5,-4,-3,-2,-1\]

#### 6.reduce()

```
from functools import reduce)
product = reduce((lambda x,y:x*y),[1,2,3,4])
```

输出24

#### 7.set

集合既不能包含重复值(其他行为与list相似)

语法：set(list)

交集：

```
print (set1.intersection(set2))
```

差集：

```
print (set1.difference(set2))
```

#### 8.三元运算符

使用举例：

```
is_fat = True
state = "fat" if is_fat else "not fat"
```

 

[《Python进阶》读书笔记(2)](http://www.calmkart.com/?p=139) [《Python进阶》读书笔记(3)](http://www.calmkart.com/?p=150)
