#!/usr/bin/env python
#coding=utf-8
'''
Created on 2015年8月11日

@author: zhguixin
'''
from urllib import urlretrieve
from urlparse import urlparse, urljoin
from os.path import splitext, dirname, exists, isdir
from htmllib import HTMLParser
from formatter import AbstractFormatter, DumbWriter
from cStringIO import StringIO
from posix import unlink
from os import makedirs
from string import find, lower
from sys import argv

class Retriever(object):
    def __init__(self,url):
        self.url = url
        self.file = self.filename(url)
    
    def filename(self,url,deffile='index.html'):
        re = urlparse(self.url,"http:",0)
        path = re[1]+re[2]
        ext = splitext(path)
        if ext[1]=='':
            if path[-1]=='/':
                path += deffile
            else:
                path += '/'+deffile
        ldir = dirname(path)
        
        if not isdir(ldir):
            if exists(ldir):
                unlink(ldir)
            makedirs(ldir)
        
        return path
        
    def download(self):
        try:
            retval = urlretrieve(self.url,self.file)
        except IOError:
            retval = ('***ERROR:invalid URL "%s"'%(self.url))
        return retval
    
    def parseAndGetLinks(self):
        parser = HTMLParser(AbstractFormatter(DumbWriter(StringIO())))
        parser.feed(open(self.file).read())
        parser.close()
        return parser.anchorlist
    
class Crawl(object):
    count = 0
    def __init__(self,url):
        self.q = [url]
        self.seen = []
        
    def getPage(self,url):
        r = Retriever(url)
        retval = r.download()
        if retval[0] == '*':
            print retval,'...skip parse'
            return
        Crawl.count += 1
        self.seen.append(url)
        dom = urlparse(url)[1]
        
        links = r.parseAndGetLinks()
    
        for eachLink in links:
            if eachLink[:4] != 'http' and find(eachLink,'://') == -1:
                eachLink = urljoin(url,eachLink)
            
            print '* ',eachLink,
            
            if find(lower(eachLink),'mailto:') != -1:
                print '...discarded,mailto link'
                continue
            
            if eachLink not in self.seen:
                if find(eachLink,dom) == -1:
                    print '...discarded,not in domain'
                else:
                    if eachLink not in self.q:
                        self.q.append(eachLink)
                        print '...new,added to Queue'
                    else:
                        print '...discarded,already in Queue'
            else:
                print '...discarded,already processed'    
    
    def run(self):
        while self.q:
            url = self.q.pop()
            self.getPage(url)
   
 
def main():
    if len(argv)>1:
        url = argv[1]
    else:
        try:
            url = raw_input('Enter starting URL: ')
        except (KeyboardInterrupt,EOFError):
            url = ''
    
    if not url:
        return
    
    robot = Crawl(url)
    robot.run() 

############################
#main method for test...
############################
if __name__ == "__main__":
    spider = Crawl("http://123.xidian.edu.cn/")
    spider.run()
#     main()
#     test = Retriever("http://123.xidian.edu.cn/")
#     retval = test.download()
#     shit = test.filename("http://123.xidian.edu.cn/")
#     links = test.parseAndGetLinks()
#     
#     print retval
#     print shit
#     print links
