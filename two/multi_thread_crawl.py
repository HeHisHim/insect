"""
多线程爬虫
"""
import sys
sys.path.append("..")

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

class CrawlBSF:
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
    cur_level = 0
    max_level = 5
    dir_name = "iterate/"
    iter_width = 50
    downloaded_urls = []

    du_md5_file_name = dir_name + "download.txt"
    du_url_file_name = dir_name + "urls.txt"

    bloom_downloaded_urls = BloomFilter(1024 * 1024 * 16, 0.01)
    bloom_url_queue = BloomFilter(1024 * 1024 * 16, 0.01)

    cur_queue = deque()
    child_queue = deque()

    def __init__(self, url):
        self.root_url = url
        self.cur_queue.append(url)

        # 创建文件夹和文件
        if not os.path.exists(self.dir_name):
            os.mkdir(self.dir_name)
            with open(self.du_url_file_name, "w"):
                pass
            with open(self.du_md5_file_name, "w"):
                pass
        
        try:
            with open(self.du_md5_file_name, "r") as fo:
                self.downloaded_urls = fo.readlines()
            for urlmd5 in self.downloaded_urls:
                self.bloom_downloaded_urls.add(urlmd5[:-2])
        except Exception as identifier:
            logger.error(identifier)