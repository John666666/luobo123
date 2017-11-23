#!/usr/bin/python
# -*-coding:utf8-*-
__author__ = 'John'

import web
import json
import logging
import sys

logger = logging.getLogger("luobo123")
my_format = logging.Formatter("%(asctime)-15s %(levelname)s %(filename)s %(lineno)s %(process)s %(message)s")
fileHandler = logging.FileHandler("luobo123.log", encoding="utf-8")
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(my_format)
logger.addHandler(fileHandler)

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
console.setFormatter(my_format)
logger.addHandler(console)

from models import DbHelper
dbHelper = DbHelper()

urls = (
    '/luobo123$', 'index',
    '/luobo123/index$', 'index',
    '/luobo123/unbind$', 'unbind',
    '/luobo123/unbind/(\w+)', 'unbind',
    '/luobo123/log$', 'log',
    '/luobo123/log/(\w+)', 'log',
)

render = web.template.render('templates', cache=False)

def response_error(code=500, msg="请求出错"):
    return response_result(code, None, msg)

def response_success(code=200, msg="请求成功", data=None):
    return response_result(code, data, msg)

def response_result(code, data, msg):
    web.header('Content-Type', 'application/json;charset=UTF-8')
    ret = {"code": code, "msg": msg, "data": data}
    return json.dumps(ret)


class index:
    def GET(self):
        return render.index()

class unbind:
    def GET(self, action=None):
        if action is None:
            return render.unbind()
        params = web.input()
        imei = params.get("imei", None)
        if imei is None:
            return response_error(msg="参数imei号是必传参数")
        if "search" == action:
            data = dbHelper.search_robot_user(imei)
            if data is None:
                return response_error(msg="查询绑定关系失败")
            return response_success(data=data)
        elif "unbind" == action:
            if dbHelper.delete_robot_user(imei):
                return response_success(msg="解绑成功")
            else:
                return response_error(msg="解绑失败")
        else:
            return response_error("不支持的操作: %s" % action)

    def POST(self, action=None):
        return self.GET(action)

class log:
    def GET(self, action=None):
        params = web.input()
        if action is None:
            return render.log()
        imei = params.get("imei", None)
        if "search" == action:
            data = dbHelper.search_log(imei)
            if data is None:
                return response_error(msg="查询日志出错")
            return response_success(data=data)
        else:
            return response_error("不支持的操作: %s" % action)

    def POST(self, action=None):
        return self.GET(action)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()

