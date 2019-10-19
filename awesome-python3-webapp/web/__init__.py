# coding=utf-8

from flask import Flask
from auth import bp
import blog
from flask_script import Manager
import time
import manage
import api
from datetime import datetime

#filter
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
    app.register_blueprint(bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(manage.bp)
    app.register_blueprint(api.bp)
    app.add_url_rule('/', endpoint='index')
    app.jinja_env.filters['datetime'] = datetime_filter
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    return app


app = create_app()
#app.debug = True
#manage = Manager(app=app)


if __name__ == '__main__':
    #manage.run()
    app.run(host='0.0.0.0', port='5000')
