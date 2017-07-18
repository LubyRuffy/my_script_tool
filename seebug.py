# -*- coding: utf-8 -*-
# @Author: bunny
# @Date:   2016-03-23 13:37:10
# @Last Modified by:   bunny
# @Last Modified time: 2016-03-29 12:13:28
import urllib2
import re
from BeautifulSoup import BeautifulSoup
import datetime

def seebug():
    all = []
    userMainUrl = "https://www.exploit-db.com/webapps/"
    req = urllib2.Request(userMainUrl)
    resp = urllib2.urlopen(req)
    respHtml = resp.read()
    songtasteHtmlEncoding = "UTF-8"
    soup = BeautifulSoup(respHtml,fromEncoding=songtasteHtmlEncoding).tbody
    for soup1 in soup.contents:
        if not soup1 == '\n':
            vulnsdate = soup1.find(attrs={"class":"date"})
            dlink1 = soup1.find(attrs={"class":"dlink"})
            app1 = soup1.find(attrs={"class":"app"})
            description1 = soup1.find(attrs={"class":"description"})
            if(vulnsdate):
                date1 = vulnsdate.string.replace('\t','').replace('\n','').replace(' ','')
                date2 = datetime.datetime.now().strftime("%Y-%m-%d")
                if date1 == date2:
                    description = description1.a.string.replace('/','')
                    dlink = dlink1.a['href']
                    app =  "https://www.exploit-db.com" + str(app1.a['href'])
                    all.append((description,dlink,app))        
    return all
                 
def main():
    all = seebug()
    for description,dlink,app in all:
        file = urllib2.urlopen(dlink)
        data = file.read()
        with open("/Users/bunny/Dropbox/seebug/" + description + ".txt", "wb") as code:     
            code.write(data)
        file1 = urllib2.urlopen(app)
        data1 = file1.read()
        with open("/Users/bunny/Dropbox/app/" + description + ".zip", "wb") as code:
            code.write(data1)

if __name__ == '__main__':
    main()
