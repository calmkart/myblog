---
title: "使用zabbix api提取趋势(trend)和历史(history)数据"
date: 2017-12-27
description: "zabbix restful api说明见官网文档 https://www.zabbix.com/documentation/4.0/zh/manual/api/reference/apiinfo 使用了github上封装好的python..."
categories: 
  - "计算机"
tags: 
  - "zabbix"
  - "运维开发"
---

zabbix restful api说明见官网文档 [https://www.zabbix.com/documentation/4.0/zh/manual/api/reference/apiinfo](https://www.zabbix.com/documentation/4.0/zh/manual/api/reference/apiinfo)

使用了github上封装好的python zabbix api,免去了自己造轮子的过程 [https://github.com/lukecyca/pyzabbix](https://github.com/lukecyca/pyzabbix) <!--more-->

这个封装的python zabbix api实现起来也比较简单，主要是用缺省的类__getattr__()方法，调用zabbix的restful api

首先用pip安装pyzabbix

```bash
pip install pyzabbix

```

具体实现获取trend和history代码如下:

```python
#---coding:utf-8---

from pyzabbix import ZabbixAPI
import time
class get_net(object):
	url = ""
	username = None
	password = None

	def __init__(self, server, user, passwd):
		self.url = "http://"+server+"/zabbix"
		self.username = user
		self.password = passwd

	def get_trend(self, info_list):
		z = ZabbixAPI(self.url)
		z.login(self.username,self.password)
		for info in info_list:
			hosts = z.host.get(filter={"host":info["ip"]})
			if hosts:
				host_id = hosts[0]["hostid"]
			print host_id
			items = z.item.get(hostids=host_id,filter={"key_":"ifHCOutOctets["+info["interface"]+"]"})[0]
			if items:
				item_id = items["itemid"]
			trend = z.trend.get(itemids=item_id)
			for td in trend:
				clock = self.get_clock(td['clock'])
				if ("20:00" in clock) or ("21:00" in clock) or ("22:00" in clock):
					print clock+"        "+str(int(td["value_avg"])*8/1048576)
					f = open(info["name"],"a")
					f.write(clock+"        "+str(int(td["value_avg"])*8/1048576))
					f.write("\n")
			f.close()

	def get_history(self, info_list):
		z = ZabbixAPI(self.url)
		z.login(self.username,self.password)
		for info in info_list:
			hosts = z.host.get(filter={"host":info["ip"]})
			if hosts:
				host_id = hosts[0]["hostid"]
			print host_id
			items = z.item.get(hostids=host_id,filter={"key_":"ifHCOutOctets["+info["interface"]+"]"})[0]
			if items:
				item_id = items["itemid"]
			history = z.history.get(itemids=item_id,time_from=1512129600)
			r_t = []
			print history
			for hs in history:
				clock = self.get_clock(hs['clock'])
				if ("20:" in clock) or ("21:" in clock) or ("22:" in clock):
					print clock+"        "+str(int(hs["value"])/1048576)
					r_t.append(clock+"        "+str(int(hs["value"])/1048576))
			r_t_str = "\n".join(r_t)
			f = open("test_history","a")
			f.write(r_t_str)
			f.close()
	
	def get_clock(self, value):
		clock = time.localtime(int(value))
		format = '%Y-%m-%d %H:%M'
		return time.strftime(format,clock)

#test = get_net("zabbix服务器IP", "user", "pass")
#test.get_trend([{"ip":"机器IP","name":"某机器","interface":"某接口名"}])
#test.get_trend(info列表，格式如上)
#test.get_history([{"ip":"机器IP","name":"某机器","interface":"某接口名"}])
#test.get_history(info列表，格式如上)

```

注： 其中get_clock()函数用于做linux时间戳转换。
