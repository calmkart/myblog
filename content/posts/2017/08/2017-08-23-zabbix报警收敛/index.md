---
title: "zabbix报警收敛"
date: 2017-08-23
categories: 
  - "计算机"
tags: 
  - "python"
  - "zabbix"
  - "报警"
---

因zabbix可能同一段时间报警过多，接受消息时如果不做收敛可能出错也不容易审查，所以需要一个报警收敛机制。 <!--more-->

实验环境分为server端与client端： server端模拟收敛程序通过TCP SOCKET连接接受zabbix报警，做收敛处理并发送； client端模拟zabbix报警程序，通过TCP SOCKET连接发送模拟的zabbix报警给server;

server端程序如下：

```
# -*- coding:utf-8 -*-
from threading import Timer
import urllib2
import socket
import threading
import re

#event_list为收敛类型数目列表
#ip_list为IP收敛字典列表
#summary为收敛类型说明列表
#keyw为正则匹配元素

class convergence(object):
	event_list = [0,0,0,0]
	summary = ['获取uptime时间失败','SNMP_cant_respond_for_5minutes错误','OK错误','流量速率异常错误']
	ip_list = [{},{},{},{}]
	keyw = ['获取uptime时间失败','SNMPcan\'trespondfor5minutes','ok','流量速度异常']
	t = None
	
	def convergence(self,event):
		temp = self.keyword(event)
		ip = self.findip(event)
		if temp != 0:
			#做报警IP收敛
			if self.ip_list[temp-1].has_key(ip):
				self.ip_list[temp-1][ip] = self.ip_list[temp-1][ip]+1
			else:
				self.ip_list[temp-1][ip] = 1
			#做报警条目收敛
			self.event_list[temp-1] = self.event_list[temp-1]+1
			if self.t == None:
				self.timer(event)
			else:
				pass
		
		else:
			#按原格式发送
			print event
			pass

	def send(self,event):
		print '目前的缓存区为'+str(self.event_list)
		if max(self.event_list) == 0:
			pass
		else:
			for i in range(0,len(event_list)):
				if self.event_list[i]==0:
					pass
				else:#发送收敛后的报警到指定位置
					content = str(event_list[i]+'次'+self.summary[i]+'(前20秒内)')
					self.event_list[i] = 0
					self.t = None
					urllib2.urlopen('http://www.calmkart.com')
					print content

	def timer(self,event):#启动定时器
		self.t = Timer(20,self.send,args=[event])
		self.t.start()
	
	def keyword(self,event):
		for i in range(0,len(self.keyw)):
			if re.search(self.keyw[i],event,flags=re.IGNORECASE) != None:
				return i+1
		return 0
	
	def findip(self,event):
		m = re.search(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])',event)
		if m is not None:
			ip = m.group()
			return str(ip)
		return '查不到IP'

test = convergence()

#tcp测试,server端，接收
host = '0.0.0.0'
port = 9001
s = socket.socket()
s.bind((host,port))
s.listen(5)

while True:
	c,addr = s.accept()
	data = c.recv(1024)
	test.convergence(data)
	
##udp测试,server端，接收
#s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#host = '10.17.16.207'
#port = 9001
#s.bind((host,port))
#
#while True:
#	data,addr = s.recvfrom(2048)
#	test.convergence(data)

```

 

clent端程序如下：

```
# --- coding:utf-8 ---
import random
from multiprocessing.connection import Client

str1 = [
	'192.168.0.1SNMP错误',
        '192.168.0.2SNMP错误',
        '192.168.0.100,OK',
        '192.168.0.101,ok',
	'192.168.0.102,流量速率异常',
	'192.168.0.103,流量速率异常',
	'192.168.0.104,获取uptime时间失败',
	'192.168.0.105,获取uptime时间失败'
] 
address = ('0.0.0.0',9001)

for i in range(0,1000):
	m = str1[random.randrange(0,11)]
	conn = Client(address)
	conn.send(m)
	conn.close

```

主要用到的工具是正则表达式做匹配

代码已上传至github,地址 [https://github.com/calmkart/Zabbix\_convergence](https://github.com/calmkart/Zabbix_convergence)

---

## 历史评论 (1 条)

*以下评论来自原 WordPress 站点，仅作存档展示。*

> **我有一个可爱的小椰子** (2017-08-29 20:39)
>
> 厉害了，过来学习一下
