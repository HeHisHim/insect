import sys
sys.path.append("..")

import pymysql
import hashlib

from logConfig import logger

class CrawlDataBaseManager:
    DB_NAME = "insect"
    SERVER_IP = "127.0.0.1"

    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host = self.SERVER_IP, 
                user = "root", 
                password = "******",
                database = self.DB_NAME,
                charset = "utf8"
            )
        except Exception as identifier:
            logger.error(identifier)
            exit(1)

    # url入库
    def enqueueUrl(self, url, depth):
        SQL = "INSERT INTO urls (url, md5Code, depth) VALUES (%s, %s, %s);"
        insertData = (url, hashlib.md5(url.encode()).hexdigest(), depth)
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(SQL, insertData)
        except Exception as identifier:
            logger.error(identifier)
            self.conn.rollback()
        else:
            self.conn.commit()

    # url出库并加读锁
    def dequeueUrl(self):
        QUERY_SQL = "SELECT id, url, depth FROM urls WHERE status = 'new' ORDER BY id ASC LIMIT 1 FOR UPDATE;"
        UPDATE_SQL = "UPDATE urls SET status = 'downloading' WHERE id = %s;"
        res = None
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(QUERY_SQL)
                if not cursor.rowcount:
                    return None
                res = cursor.fetchone()
                cursor.execute(UPDATE_SQL, res[0])
                return res
        except Exception as identifier:
            logger.error(identifier)
            self.conn.rollback()
            return None
        finally:
            self.conn.commit()

    # 设置url状态为done
    def finishUrl(self, id):
        SQL = "UPDATE urls SET status = 'done' WHERE id = %s;"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(SQL, id)
        except Exception as identifier:
            logger.error(identifier)
            self.conn.rollback()
        else:
            self.conn.commit()

if __name__ == "__main__":
    pass
