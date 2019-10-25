# coding=utf-8

#from flask import Flask
#from flask_script import Manager
from gevent.pywsgi import WSGIServer

from app import create_app


app = create_app()
#app.debug = True
#manage = Manager(app=app)


if __name__ == '__main__':
    #manage.run()
    #app.run(host='0.0.0.0', port='5000')
    WSGIServer(('0.0.0.0', 5000), app).serve_forever()
