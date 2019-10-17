#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' url handlers '

import re, time, json, logging, hashlib
import markdown2

from aiohttp import web

from apis import Page, APIValueError, APIResourceNotFoundError
from flask import render_template, request
from models import User, Comment, Blog, next_id
from config import configs
from pony.orm import *

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def cookie2user():
    '''
    Parse cookie and load user if cookie is valid.
    '''
    cookie_str = request.cookies.get(COOKIE_NAME)
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        with db_session:
            user = select(u for u in User if u.id==uid)[:][0]
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        #user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


'''
@app.route('/manage/blogs/edit', methods=['GET'])
def manage_edit_blog(*, id):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' %id
    }


@app.route('/manage/users', methods=['GET'])
def manage_users(*, page='1'):
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }'''


'''
@app.route('/api/users', methods=['POST'])
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await selece(u for u in User if User.email == email)[:]
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    with db_session:
        await User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode(
            'utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' %
                                         hashlib.md5(email.encode('utf-8')).hexdigest())
        commit()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@app.route('/api/blogs', methods=['GET'])
async def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    with db_session:
        num = await select(count(b.id) for b in Blog)
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    with db_session:
        blogs = await select(b for b in Blog).order_by('created_at desc')[p.offset: p.limit]
    return dict(page=p, blogs=blogs)


@app.route('/api/blogs/<int:id>', methods=['GET'])
async def api_get_blog(*, id):
    with db_session:
        blog = await select(b for b in Blog if Blog.id == id)
    return blog


@app.route('/api/blogs', methods=['POST'])
async def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    with db_session:
        blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
             name=name.strip(), summary=summary.strip(), content=content.strip())
    return blog


@app.route('/api/blogs/<int:id>', methods=['POST'])
async def api_update_blog(id, request, *, name, summary, content):
    check_admin(request)
    with db_session:
        blog = await Blog.get(id=id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')
    with db_session:
        blog.name = name.strip()
        blog.summary = summary.strip()
        blog.content = content.strip()
        await commit()
    return blog


@app.route(('/api/blogs/<int:id>/delete'), methods=['POST'])
async def api_delete_blog(request, *, id):
    check_admin(request)
    blog = await Blog.find(id)
    with db_session:
        Blog.get(id=id).delete()
        await commit
    return dict(id=id)


@app.route('/api/comments', methods=['GET'])
async def api_get_comments(*, page='1'):
    page_index = get_page_index(page)
    with db_session:
        num = await select(count(c.id) for c in Comment)
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    with db_session:
        comments = await select(c for c in Comment).order_by('created_at desc')[p.offset: p.limit]
    return dict(page=p, comments=comments)


@app.route('/api/blogs/<int:id>/comments', methods=['GET'])
async def api_create_comment(id, request, *, content):
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip():
        raise APIValueError('content')
    with db_session:
        blog = await Blog.get(id=id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    with db_session:
        comment = await Comment(blog_id=blog.id, user_id=user.id, user_image=user.image, content=content.strip())
        await commit()
    return comment


@app.route('/api/comments/<int:id>/delete', methods=['POST'])
async def api_delete_comments(id, request):
    check_admin(request)
    with db_session:
        c = await Comment.get(id=id)
    if c is None:
        raise APIResourceNotFoundError
    with db_session:
        await c.delete()
        await commit()
    return dict(id=id)


@app.route('/api/users', methods=['GET'])
async def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    with db_session:
        num = await select(count(User) for u in User)
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    with db_session:
        users = await select(u for u in User).order_by('created_at desc')[p.offset: p.limit]
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)

'''