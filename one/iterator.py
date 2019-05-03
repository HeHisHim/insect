from urllib import request as urllibRequest
from urllib import error as urllibError
from collections import deque
import json
from lxml import etree
import httplib2
import hashlib
from pybloom import BloomFilter
import os
import requests
from logConfig import logger

ignore_file = [".jpg", ".gif"]

request_headers = {
    "host": "i.jandan.net",
    "connection": "keep-alive",
    "cache-control": "no-cache",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}

root_url = "http://jandan.net/"
max_level = 5
dir_name = "iterate/"
iter_width = 3

if not os.path.exists(dir_name):
    os.mkdir(dir_name)

downloaded_url_file_name = dir_name + "download.txt"

with open(downloaded_url_file_name, "a+") as du_file:
    downloaded_urls = du_file.readlines()

def getPageContent(cur_url, cur_level):
    logger.info("downloading %s at level %d" % (cur_url, cur_level))
    try:
        req = requests.get(cur_url, headers = request_headers)
        html_page = req.content.decode("utf8")
        # 取 http://之后的字符命名
        filename = cur_url[7:].replace("/", "_")
        if filename.endswith(".html"):
            with open("%s%s" % (dir_name, filename), "w") as fo:
                fo.write(html_page)
        else:
            with open("%s%s.html" % (dir_name, filename), "w") as fo:
                fo.write(html_page)
    except Exception as identifier:
        logger.error(identifier)

    hmd5url = hashlib.md5(cur_url.encode()).hexdigest()
    downloaded_urls.append(hmd5url)

    with open(downloaded_url_file_name, "a+") as du_file:
        du_file.write(hmd5url + "\r\n")

    html = etree.HTML(html_page.lower())
    if html is None:
        logger.error("None Page")
        return
    hrefs = html.xpath(u"//a")

    if cur_level == max_level:
        return
    
    page_index = 0
    for href in hrefs:
        try:
            if "href" in href.attrib:
                val = href.attrib["href"]
                # 剔除 javascript的链接
                if -1 != val.find("javascript:"):
                    continue
                if False == val.startswith("http://"):
                    if val.startswith("/"):
                        val = "http://jandan.net" + val
                    else:
                        continue
                if val[-4:] in ignore_file:
                    continue
                if "/" == val[-1]:
                    val = val[0:-1]
                if hashlib.md5(val.encode()).hexdigest() not in downloaded_urls:
                    getPageContent(val, cur_level + 1)
                    page_index += 1
                    if page_index == iter_width:
                        logger.info("pageIndex: %s" % page_index)
                        break
                else:
                    logger.info("Skip %s" % val)
        except Exception as identifier:
            continue

getPageContent(root_url, 0)

