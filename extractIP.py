# -*- coding=utf8 -*-
"""
    从网上爬取HTTPS代理
"""
import re
import sys
import time
import Queue
import logging
import requests
import threading
from pyquery import PyQuery
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
 
 
#logging.basicConfig(
#    level=logging.DEBUG,
#    format="[%(asctime)s] %(levelname)s: %(message)s")
 
class Worker(threading.Thread):  # 处理工作请求
    def __init__(self, workQueue, resultQueue, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue
 
    def run(self):
        while 1:
            try:
                callable, args, kwds = self.workQueue.get(False)  # get task
                res = callable(*args, **kwds)
                self.resultQueue.put(res)  # put result
            except Queue.Empty:
                break
 
 
class WorkManager:  # 线程池管理,创建
    def __init__(self, num_of_workers=10):
        self.workQueue = Queue.Queue()  # 请求队列
        self.resultQueue = Queue.Queue()  # 输出结果的队列
        self.workers = []
        self._recruitThreads(num_of_workers)
 
    def _recruitThreads(self, num_of_workers):
        for i in range(num_of_workers):
            worker = Worker(self.workQueue, self.resultQueue)  # 创建工作线程
            self.workers.append(worker)  # 加入到线程队列
 
    def start(self):
        for w in self.workers:
            w.start()
 
    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()  # 从池中取出一个线程处理请求
            worker.join()
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append(worker)  # 重新加入线程池中
        #logging.info('All jobs were complete.')
 
    def add_job(self, callable, *args, **kwds):
        self.workQueue.put((callable, args, kwds))  # 向工作队列中加入请求
 
    def get_result(self, *args, **kwds):
        return self.resultQueue.get(*args, **kwds)
 
def check_proxies(ip,port):
    """
    检测代理存活率
    分别访问v2ex.com以及guokr.com
    """
    proxies={'http': 'http://'+str(ip)+':'+str(port)}
    try:
        r0 = requests.get('http://v2ex.com', proxies=proxies,timeout=30,verify=False)
        r1 = requests.get('http://www.guokr.com', proxies=proxies,timeout=30,verify=False)
 
        if r0.status_code == requests.codes.ok and r1.status_code == requests.codes.ok and "09043258" in r1.content and "15015613" in r0.content:
            #r0.status_code == requests.codes.ok and r1.status_code == requests.codes.ok and 
            print ip,port
            return True
        else:
            return False
 
    except Exception, e:
        pass
        #sys.stderr.write(str(e))
        #sys.stderr.write(str(ip)+"\t"+str(port)+"\terror\r\n")
        return False
 
def get_ip181_proxies():
    """
    http://www.ip181.com/获取HTTP代理
    """
    proxy_list = []
    try:
        html_page = requests.get('http://www.ip181.com/',timeout=60,verify=False,allow_redirects=False).content.decode('gb2312')
        jq = PyQuery(html_page)
        for tr in jq("tr"):
            element = [PyQuery(td).text() for td in PyQuery(tr)("td")]
            if 'HTTP' not in element[3]:
                continue
 
            result = re.search(r'\d+\.\d+', element[4], re.UNICODE)
            if result and float(result.group()) > 5:
                continue
            #print element[0],element[1]
            proxy_list.append((element[0], element[1]))
    except Exception, e:
        sys.stderr.write(str(e))
        pass
 
    return proxy_list
 
def get_kuaidaili_proxies():
    """
    http://www.kuaidaili.com/获取HTTP代理
    """
    proxy_list = []
    for m in ['inha', 'intr', 'outha', 'outtr']:
        try:
            html_page = requests.get('http://www.kuaidaili.com/free/'+m,timeout=60,verify=False,allow_redirects=False).content.decode('utf-8')
            patterns = re.findall(r'(?P<ip>(?:\d{1,3}\.){3}\d{1,3})</td>\n?\s*<td.*?>\s*(?P<port>\d{1,4})',html_page)
            for element in patterns:
                #print element[0],element[1]
                proxy_list.append((element[0], element[1]))
        except Exception, e:
            sys.stderr.write(str(e))
            pass
 
    for n in range(0,11):
        try:
            html_page = requests.get('http://www.kuaidaili.com/proxylist/'+str(n)+'/',timeout=60,verify=False,allow_redirects=False).content.decode('utf-8')
            patterns = re.findall(r'(?P<ip>(?:\d{1,3}\.){3}\d{1,3})</td>\n?\s*<td.*?>\s*(?P<port>\d{1,4})',html_page)
            for element in patterns:
                #print element[0],element[1]
                proxy_list.append((element[0], element[1]))
        except Exception, e:
            sys.stderr.write(str(e))
            pass
 
    return proxy_list
 
def get_66ip_proxies():
    """
    http://www.66ip.com/ api接口获取HTTP代理
    """
    urllists = [
        'http://www.proxylists.net/http_highanon.txt',
        'http://www.proxylists.net/http.txt',
        'http://www.66ip.cn/nmtq.php?getnum=1000&anonymoustype=%s&proxytype=2&api=66ip',
        'http://www.66ip.cn/mo.php?sxb=&tqsl=100&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1'
        ]
    proxy_list = []
    for url in urllists:
        try:
            html_page = requests.get(url,timeout=60,verify=False,allow_redirects=False).content.decode('gb2312')
            patterns = re.findall(r'((?:\d{1,3}\.){1,3}\d{1,3}):([1-9]\d*)',html_page)
            for element in patterns:
                #print element[0],element[1]
                proxy_list.append((element[0], element[1]))
        except Exception, e:
            sys.stderr.write(str(e))
            pass
 
    return proxy_list
 
 
def get_proxy_sites():
    wm = WorkManager(20)
    proxysites = []
    proxysites.extend(get_ip181_proxies())
    proxysites.extend(get_kuaidaili_proxies())
    proxysites.extend(get_66ip_proxies())
 
    for element in proxysites:
        wm.add_job(check_proxies,str(element[0]),str(element[1]))
    wm.start()
    wm.wait_for_complete()
 
 
if __name__ == '__main__':
    try:
        get_proxy_sites()
    except Exception as exc:
        print(exc)