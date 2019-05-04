import sys
sys.path.append("..")

import pymysql
import hashlib

import logConfig

class CrawlDataBaseManager:
    DB_NAME = "insect"
    SERVER_IP = "127.0.0.1"

    TABLES = {}

    def __init__(self, max_thread = 1):
        try:
            self.conn = pymysql.connect(
                host = self.SERVER_IP, 
                user = "root", 
                password = "*****",
                database = "abc",
                charset = "utf8"
            )
        except Exception as identifier:
            logConfig.logger.error(identifier)
            exit(1)

    def check(self):
        SQL = "SELECT * FROM urls;"
        res = 100
        data = 200
        try:
            with self.conn.cursor() as cursor:
                res = cursor.execute(SQL)
                data = cursor.fetchone()
        except Exception as identifier:
            logConfig.logger.error(identifier)
            logConfig.logger.error("mysql boom!")
        
        print("res: ", res)
        print("data: ", data)

x = CrawlDataBaseManager()
x.check()
