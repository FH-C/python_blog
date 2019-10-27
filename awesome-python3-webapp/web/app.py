# coding=utf-8
from datetime import datetime
import time

from flask import Flask

import api
import manage
import blog
import auth

#filter 日志创建时间
def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


def create_app():
    app = Flask(__name__)
    ##注册蓝图
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(manage.bp)
    app.register_blueprint(api.bp)
    app.add_url_rule('/', endpoint='index')
    app.jinja_env.filters['datetime'] = datetime_filter
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    return app