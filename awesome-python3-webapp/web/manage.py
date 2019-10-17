# coding=utf-8
import functools

import hashlib, json
import logging
import re

from flask import Blueprint, flash, g, redirect, render_template
from pony.orm import *

from handlers import COOKIE_NAME, user2cookie
from models import db, User, Comment, Blog, next_id

from apis import APIValueError, APIError
from flask import request
from apis import Page
from handlers import get_page_index


from handlers import cookie2user

from auth import is_admin

bp = Blueprint('manage', __name__, url_prefix='/manage')


@bp.route('/', methods=['GET'])
@is_admin
def manage():
    return redirect('/manage/comments')


@bp.route('/blogs', methods=['GET'])
@is_admin
def manage_blogs():
    page = request.args.get('page', '1')
    page_index = get_page_index(page)
    with db_session:
        num = len(select(b for b in Blog)[:])
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    with db_session:
        blogs = select(b for b in Blog).order_by(Blog.created_at)[p.offset: p.limit+p.offset]
    user = cookie2user()
    return render_template('manage_blogs.html', page_index=page_index, user=user, page=p)


@bp.route('/blogs/create', methods=['GET', 'POST'])
@is_admin
def blog_create():
    user = cookie2user()
    if request.method == 'POST':
        blog_info = request.json
        name = blog_info['name']
        summary = blog_info['summary']
        content = blog_info['content']
        if not name or not name.strip():
            raise APIValueError('name', 'name cannot be empty.')
        if not summary or not summary.strip():
            raise APIValueError('summary', 'summary cannot be empty.')
        if not content or not content.strip():
            raise APIValueError('content', 'content cannot be empty.')
        with db_session:
            blog = Blog(user_id=user.id, user_name=user.name, user_image=user.image,
                        name=name.strip(), summary=summary.strip(), content=content.strip())
            id = blog.id
        #return render_template('manage_blogs.html', page_index=1, user=user, id=id, action='/api/blogs/%s' % id)
            blog = Blog.get(id=id)
            return blog.to_dict()
    else:
        return render_template('manage_blog_edit.html', user=user)


@bp.route('/blogs/edit', methods=['GET', 'POST'])
@is_admin
@db_session
def api_update_blog():
    id = request.args.get('id')
    user = cookie2user()
    blog = Blog.get(id=id)
    if request.method == 'POST':
        blog_info = request.json
        name = blog_info['name']
        summary = blog_info['summary']
        content = blog_info['content']
        if not name or not name.strip():
            raise APIValueError('name', 'name cannot be empty.')
        if not summary or not summary.strip():
            raise APIValueError('summary', 'summary cannot be empty.')
        if not content or not content.strip():
            raise APIValueError('content', 'content cannot be empty.')
        blog.name = name.strip()
        blog.summary = summary.strip()
        blog.content = content.strip()
        commit()
        return blog.to_dict()
    else:
        return render_template('manage_blog_edit.html', user=user, name=blog.name, summary=blog.summary, content=blog.content)


@bp.route('/blogs/<id>/delete', methods=['POST'])
@is_admin
def api_delete_blog(id):
    with db_session:
        blog = Blog.get(id=id)
        blog.delete()
    return dict(id=id)


@bp.route('/users', methods=['GET', 'POST'])
@is_admin
def manage_users():
    page = request.args.get('page', '1')
    page_index = get_page_index(page)
    with db_session:
        num = len(select(u for u in User)[:])
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    with db_session:
        users = select(u for u in User).order_by(User.created_at)[p.offset: p.limit+p.offset]
    user = cookie2user()
    return render_template('manage_users.html', page_index=page_index, user=user)


@bp.route('/comments', methods=['GET', 'POST'])
@is_admin
def manage_comments(*, page='1'):
    page = request.args.get('page', '1')
    page_index = get_page_index(page)
    with db_session:
        num = len(select(c for c in Comment)[:])
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    with db_session:
        comments = select(c for c in Comment).order_by(Comment.created_at)[p.offset: p.limit+p.offset]
    user=cookie2user()
    return render_template('manage_comments.html', page_index=page_index, user=user)


@bp.route('/comments/<id>/delete', methods=['POST'])
@is_admin
def api_delete_comment(id):
    with db_session:
        comment = Comment.get(id=id)
        comment.delete()
    return dict(id=id)