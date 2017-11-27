#!/usr/bin/python
# -*-coding:utf8-*-
__author__ = 'John'

import MySQLdb as mysql
import logging
import sys
logger = logging.getLogger("luobo123")
import json
from json_utils import JSONEncoder
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

class DbHelper:
    def __init__(self):
        try:
            self.api_db_pool = PooledDB(mysql, mincached=1, maxcached=3, host="localhost", user="root",
                                        passwd="Lu0b0tec", db="lb2api", use_unicode=True, charset="utf8")
            self.nlu_db_pool = PooledDB(mysql, mincached=1, maxcached=3, host="localhost", user="root",
                                        passwd="Lu0b0tec", db="nlu_cloud", use_unicode=True, charset="utf8")
        except Exception, e:
            logger.error("get database conn fail: %s" % e)
            sys.exit(1)

    def connApiDB(self):
        self.api_conn = self.api_db_pool.connection()
        self.api_cursor = self.api_conn.cursor(DictCursor)

    def closeApiDB(self):
        self.api_cursor.close()
        self.api_conn.close()

    def connNluDB(self):
        self.nlu_conn = self.nlu_db_pool.connection()
        self.nlu_cursor = self.nlu_conn.cursor(DictCursor)

    def closeNluDB(self):
        self.nlu_cursor.close()
        self.nlu_conn.close()

    def search_log(self, imei):
        try:
            self.connNluDB()
            sql = "SELECT req_time,resp_time,req_content,domain,intent,params from intent_analysis_log where user_id = %s order by id desc limit 50;"
            self.nlu_cursor.execute(sql, (imei,))
            data = self.nlu_cursor.fetchall()
            return json.dumps(data, cls=JSONEncoder)
        except Exception, e:
            logger.error("search_log error. %s" % e)
            return None
        finally:
            self.closeNluDB()

    def search_robot_user(self, imei):
        try:
            self.connApiDB()
            sql = "SELECT racc,uacc,role,ualias,ralias,status,banding_date as binding_date, unbanding_date as unbinding_date FROM robot_user WHERE racc = %s;"
            self.api_cursor.execute(sql, (imei,))
            data = self.api_cursor.fetchall()
            return json.dumps(data, cls=JSONEncoder, ensure_ascii=True)
        except Exception, e:
            logger.error("search_robot_user error. %s" % e)
            return None
        finally:
            self.closeApiDB()

    def delete_robot_user(self, imei):
        try:
            self.connApiDB()
            sql = "DELETE FROM robot_user WHERE racc = %s;"
            self.api_cursor.execute(sql, (imei,))
            n = self.api_cursor.rowcount
            self.api_conn.commit()
            if n > 0:
                return True
            else:
                return False
        except Exception, e:
            self.api_conn.rollback()
            logger.error("delete_robot_user error. %s" % e)
        finally:
            self.closeNluDB()



