#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This example shows how to build a proxy based on mitmproxy's Flow
    primitives.
    Heads Up: In the majority of cases, you want to use inline scripts.
    Note that request and response messages are not automatically replied to,
    so we need to implement handlers to do this.
"""


from mitmproxy import controller, options,flow
from mitmproxy.proxy import ProxyServer, ProxyConfig
import datetime
from urlparse import urlparse
import pymongo
import re


class MyMaster(flow.FlowMaster):
    def run(self):
        self.db_init()
        try:
            flow.FlowMaster.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    @controller.handler
    def request(self, flow):
        #print(f)
        return flow

    @controller.handler
    def response(self, flow):
        #print(flow.request.host)
        # f = flow.FlowMaster.handle_intercept(self,f)
        # print(f)
        if flow:
            self.db_insert(flow)
            print("sussed")
        return flow
        # print("response", f)


    def db_init(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client["scan"]
        self.coll = self.db["url_info"]
        self.to_be_scan = self.db['list']
        return

    #存储数据
    def db_insert(self, flow):
        now = datetime.datetime.now()
        if flow:
            insert_dict = {
                'status': 9,
                'domain': flow.request.host,
                'client_ip': flow.client_conn.address.host,
                'scheme': flow.request.scheme,
                'method': flow.request.method,
                'time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'target': flow.request.url,
                'flag': 0,
                'request': {
                    'request_data': flow.request.content,
                    'headers': dict(flow.request.headers),
                },
                'response': {
                    'request_url': flow.request.url,
                    'status_code': flow.response.status_code,
                    'headers': dict(flow.response.headers)
                }
            }
            self.coll.insert(insert_dict)
            print 'scan_target: ' + flow.request.url
        else:
            print("fuck")
    
def proxy_start():
    #opts = options.Options(cadir="~/.mitmproxy/")
    opts = options.Options(listen_port=8088)
    config = ProxyConfig(opts)
    server = ProxyServer(config)
    # pport = int(proxy_port)
    # config = proxy.ProxyConfig(options=)
    state = flow.State()
    #server = ProxyServer(config)
    print 'Express started on http://localhost:8088; press Ctrl-C to terminate.'
    m = MyMaster(opts,server, state)
    m.run()

proxy_start()