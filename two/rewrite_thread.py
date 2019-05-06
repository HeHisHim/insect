"""
继承线程来写爬虫任务
"""
import sys
sys.path.append("..")
import time

from collections import deque
import json
from lxml import etree
import httplib2
import hashlib
import os
import requests
import threading
from multiprocessing import Process
from logConfig import logger
from dbmanager import CrawlDataBaseManager

CRAWL_DELAY = 0.6

class CrawlBSF(threading.Thread):
    request_headers = {
        "connection": "keep-alive",
        "cache-control": "no-cache",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    dir_name = "iterate/"
    du_md5_file_name = dir_name + "download.txt"
    du_url_file_name = dir_name + "urls.txt"
    ignore_file = [".jpg", ".gif"]
    

    def __init__(self, cur_url, id, depth, dbmanager):
        self.cur_url = cur_url
        self.id = id
        self.depth = depth
        self.dbmanager = dbmanager
        self.flag = True
        self.thLock = threading.Lock()
        threading.Thread.__init__(self)

    def run(self):
        self.getPageContent()

    def stop(self):
        self.flag = False

    def getPageContent(self):
        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)
            with open(self.du_url_file_name, "w"):
                pass
            with open(self.du_md5_file_name, "w"):
                pass
        logger.info("downloading %s at level %s" % (self.cur_url, self.depth))
        try:
            req = requests.get(self.cur_url)
            html_page = req.content.decode("utf8")
            if self.cur_url.startswith("https"):
                filename = self.cur_url[8:].replace("/", "_")
            else:
                filename = self.cur_url[7:].replace("/", "_")
            if filename.endswith(".html"):
                with open("%s%s" % (self.dir_name, filename), "w") as fo:
                    fo.write(html_page)
            else:
                with open("%s%s.html" % (self.dir_name, filename), "w") as fo:
                    fo.write(html_page)
        except Exception as identifier:
            logger.error("1")
            logger.error(identifier)
            with self.thLock:
                self.dbmanager.finishUrl(self.id)
            return None

        dumd5 = hashlib.md5(self.cur_url.encode()).hexdigest()
        with open(self.du_md5_file_name, "a") as fo:
            fo.write(dumd5 + "\r\n")
        with open(self.du_url_file_name, "a") as fo:
            fo.write(self.cur_url + "\r\n")

        html = etree.HTML(html_page.lower())
        if html is None:
            logger.error("2")
            logger.error("None Page")
            return
        hrefs = html.xpath(u"//a")

        for href in hrefs:
            try:
                if "href" in href.attrib:
                    val = href.attrib["href"]
                    if -1 != val.find("javascript:"):
                        continue
                    elif val[-4:] in self.ignore_file:
                        continue
                    elif not (val.startswith("http://") or val.startswith("https://")):
                        if val.startswith("/"):
                            val = "https://www.sina.com.cn/" + val
                        else:
                            continue
                    elif "/" == val[-1]:
                        val = val[0:-1]
                    with self.thLock:
                        self.dbmanager.enqueueUrl(val, int(self.depth) + 1)
            except Exception as identifier:
                # logger.error("3")
                # logger.error(identifier)
                continue

def main():
    max_num_thread = 5
    dbmanager = CrawlDataBaseManager()
    dbmanager.enqueueUrl("https://www.sina.com.cn/", 0)

    is_root_page = True
    threads = []

    while True:
        curtask = dbmanager.dequeueUrl()
        if not curtask:
            for th in threads:
                th.join()
            break

        if is_root_page:
            rootCrawl = CrawlBSF(curtask[1], curtask[0], curtask[2], dbmanager)
            rootCrawl.getPageContent()
            is_root_page = False
        else:
            while True:
                for th in threads:
                    if not th.is_alive():
                        logger.info("remove who: %s", th)
                        threads.remove(th)
                
                if max_num_thread <= len(threads):
                    time.sleep(CRAWL_DELAY)
                    continue
                
                try:
                    th = CrawlBSF(curtask[1], curtask[0], curtask[2], dbmanager)
                    threads.append(th)
                    th.setDaemon(True)
                    logger.info("threads info: %d" % len(threads))
                    for x in threads:
                        logger.info("thread inner info %s" % x)
                    th.start()
                    time.sleep(CRAWL_DELAY)
                    break
                except Exception as identifier:
                    logger.error("4")
                    logger.error(identifier)

if __name__ == "__main__":
    main()