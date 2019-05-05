"""
多线程/进程爬虫 + mysql数据库
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

ignore_file = [".jpg", ".gif"]
# 设置延迟, 太过频繁访问目标站点
CRAWL_DELAY = 0.6

request_headers = {
    "connection": "keep-alive",
    "cache-control": "no-cache",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}

cur_level = 0
max_level = 5
dir_name = "iterate/"
iter_width = 50
num_downloaded_pages = 0
downloaded_urls = []

dbmanager = CrawlDataBaseManager()

du_md5_file_name = dir_name + "download.txt"
du_url_file_name = dir_name + "urls.txt"


def getPageContent(cur_url, id, depth):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        with open(du_url_file_name, "w"):
            pass
        with open(du_md5_file_name, "w"):
            pass
    logger.info("downloading %s at level %s" % (cur_url, depth))
    try:
        req = requests.get(cur_url)
        html_page = req.content.decode("utf8")
        if cur_url.startswith("https"):
            filename = cur_url[8:].replace("/", "_")
        else:
            filename = cur_url[7:].replace("/", "_")
        if filename.endswith(".html"):
            with open("%s%s" % (dir_name, filename), "w") as fo:
                fo.write(html_page)
        else:
            with open("%s%s.html" % (dir_name, filename), "w") as fo:
                fo.write(html_page)
    except Exception as identifier:
        logger.error("1")
        logger.error(identifier)
        return None

    dumd5 = hashlib.md5(cur_url.encode()).hexdigest()
    downloaded_urls.append(dumd5)
    with open(du_md5_file_name, "a") as fo:
        fo.write(dumd5 + "\r\n")
    with open(du_url_file_name, "a") as fo:
        fo.write(cur_url + "\r\n")
    
    global num_downloaded_pages
    num_downloaded_pages += 1

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
                elif val[-4:] in ignore_file:
                    continue
                elif not (val.startswith("http://") or val.startswith("https://")):
                    if val.startswith("/"):
                        val = "https://www.sina.com.cn/" + val
                    else:
                        continue
                elif "/" == val[-1]:
                    val = val[0:-1]
                dbmanager.enqueueUrl(val, int(depth) + 1)
        except Exception as identifier:
            # logger.error("3")
            # logger.error(identifier)
            continue

def main():
    max_num_thread = 5

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
            getPageContent(curtask[1], curtask[0], curtask[2])
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
                    th = threading.Thread(target = getPageContent, args = (curtask[1], curtask[0], curtask[2]))
                    # th = Process(target = getPageContent, args = (curtask[1], curtask[0], curtask[2]))
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