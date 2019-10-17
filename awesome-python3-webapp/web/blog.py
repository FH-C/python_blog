# coding=utf-8

from flask import Blueprint, render_template
from pony.orm import *
from models import db, User, Comment, Blog, next_id

from handlers import get_page_index
from apis import Page

from handlers import cookie2user
import markdown2
from handlers import text2html


bp = Blueprint('blog', __name__)


@bp.route('/')
def index(*, page='1'):
    page_index = get_page_index(page)
    with db_session:
        num = len(select(b for b in Blog)[:])
    page = Page(num, page_index)
    if num == 0:
        blogs = []
    else:
        with db_session:
            blogs = select(b for b in Blog).order_by(desc(Blog.created_at))[page.offset: page.limit]
    user = cookie2user()
    return render_template('blogs.html', page=page, blogs=blogs, user=user)


@bp.route('/blog/<id>', methods=['GET'])
def get_blog(id):
    with db_session:
        blog = Blog.get(id=id)
        comments = select(c for c in Comment if c.blog_id==id).order_by(desc(Comment.created_at))[:]
        blog.html_content = markdown2.markdown(blog.content)
        for c in comments:
            c.html_content = text2html(c.content)
    user = cookie2user()
    return render_template('blog.html', blog=blog, comments=comments, user=user)


