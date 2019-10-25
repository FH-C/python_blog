# coding=utf-8
import functools

import hashlib, json
import logging
import re

from flask import (
    Blueprint, redirect, render_template, request,
    make_response)
from pony.orm import *
from functools import wraps

from handlers import COOKIE_NAME, user2cookie, cookie2user
from models import db, User, Comment, Blog, next_id
from apis import APIValueError, APIError

bp = Blueprint('auth', __name__, url_prefix='/auth')
db.generate_mapping(check_tables=True, create_tables=False)
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_info = request.json
        name = user_info['name']
        email = user_info['email']
        passwd = user_info['passwd']
        if not name or not name.strip():
            raise APIValueError('name')
        if not email or not _RE_EMAIL.match(email):
            raise APIValueError('email')
        if not passwd or not _RE_SHA1.match(passwd):
            raise APIValueError('passwd')
        with db_session:
            users = select(u for u in User if User.email == email)[:]
        if len(users) > 0:
            raise APIError('register:failed', 'email', 'Email is already in use.')
        uid = next_id()
        #密码加密
        sha1_passwd = '%s:%s' % (uid, passwd)
        with db_session:
            User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                    image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest(), admin=Flase)
            commit()
        with db_session:
            user = User.get(id=uid)
        #with db_session:
        # make session cookie:
        #r = Response(json.dumps({'a': 1, 'b': 1}), content_type='application/json')
        #r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
        response = make_response(json.dumps({'id': user.id, 'email': user.email, 'passwd': '******',
                                             'admin': user.admin, 'name': user.name,'image': user.image,
                                             'create_at': user.created_at}))
        #设置Cookie
        response.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
        response.headers['Content-Type'] = 'application/json'
        return response

    return render_template('register.html')


@bp.route('/signin', methods=['GET', 'POST'])
def signin(*, page='1'):
    if request.method == 'POST':
        user_info = request.json
        email = user_info['email']
        passwd = user_info['passwd']
        if not email:
            raise APIValueError('email', 'Invalid email.')
        if not passwd:
            raise APIValueError('passwd', 'Invalid password.')
        with db_session:
            users = select(u for u in User if u.email == email)[:]
        if len(users) == 0:
            raise APIValueError('email', 'Email not exist.')
        user = users[0]
        #session['username'] = user.name
        # check passwd:
        sha1 = hashlib.sha1()
        sha1.update(user.id.encode('utf-8'))
        sha1.update(b':')
        sha1.update(passwd.encode('utf-8'))
        if user.passwd != sha1.hexdigest():
            raise APIValueError('passwd', 'Invalid password.')
        # authenticate ok, set cookie:
        response = make_response(json.dumps({'id': user.id, 'email': user.email, 'passwd': '******',
                                             'admin': user.admin, 'name': user.name,'image': user.image,
                                             'create_at': user.created_at}))

        response.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
        #response.headers['Content-Type'] = 'application/json'
        return response

    return render_template('signin.html')


@bp.route('/signout', methods=['GET'])
def signout():
    '''referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')'''
    response = make_response(redirect('/'))
    response.delete_cookie(COOKIE_NAME)
    logging.info('user signed out.')
    return response

'''
@bp.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':

    return render_template('user_edit.html')
'''

def is_login(func):
    @wraps(func)
    def check_login(*args,**kwargs):
        user = cookie2user()
        with db_session:
            if user:
                return func(*args,**kwargs)
            else:
                return redirect('/')
    return check_login


def is_admin(func):
    @wraps(func)
    def check_admin(*args,**kwargs):
        user = cookie2user()
        with db_session:
            if user and user.admin:
                return func(*args,**kwargs)
            else:
                return redirect('/')
    return check_admin