import uuid
import time

from pony.orm import *


def next_id():
    return '%015d%s000' % (int(time.time()*1000), uuid.uuid4().hex)


db = Database('mysql', host='localhost', user='www-data', passwd='www-data', db='awesome')


class User(db.Entity):
    _table_ = 'users'
    id = PrimaryKey(str, 50, default=next_id)
    email = Required(str, 50)
    passwd = Required(str, 50)
    admin = Required(bool)
    name = Required(str, 50)
    image = Required(str, 500)
    created_at = Required(float, default=time.time)


class Blog(db.Entity):
    _table_ = 'blogs'
    id = PrimaryKey(str, 50, default=next_id)
    user_id = Required(str, 50)
    user_name = Required(str, 50)
    user_image = Required(str, 500)
    name = Required(str, 50)
    summary = Required(str, 200)
    content = Required(LongStr)
    created_at = Required(float, default=time.time)


class Comment(db.Entity):
    _table_ = 'comments'
    id = PrimaryKey(str, 50, default=next_id)
    blog_id = Required(str, 50)
    user_id = Required(str, 50)
    user_name = Required(str, 50)
    user_image = Required(str, 500)
    content = Required(LongStr)
    created_at = Required(float, default=time.time)

