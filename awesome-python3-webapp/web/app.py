# !user/bin/env python3
# -*- coding: utf-8 -*-
from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.Response(text='awsome')
    
@routes.get('/hello/{name}')
async def hello(request):
    text = '<h1>hello, %s!</h1>' % request.match_info['name']
    return web.Response(body=text.encode('utf-8'), content_type='text/html')


app = web.Application()
app.add_routes(routes)
web.run_app(app, host='127.0.0.1', port=9000)