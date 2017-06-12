# coding=utf-8
import redis
import os
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import FileSystemLoader, Environment
from werkzeug.routing import Rule, Map

class Shortly(object):
    def __init__(self, config):
        self.redis = redis.Redis(config['redis_host'], config['redis_port'], password=config['redis_pass'])
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)
        self.url_map = Map([
            Rule(r'/', endpoint='index'),
            Rule(r'/add', endpoint='add')
        ])

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except NotFound:
            return self.render_template('error.html')
        except HTTPException as e:
            return e

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')

    def on_index(self, request):
        info = self.redis.lrange('string_list', 0, self.redis.llen('string_list'))
        return self.render_template('index.html', info=info)

    def on_add(self, request):
        if request.method == 'POST':
            string_text = request.form['string_text']
            self.redis.lpush('string_list', string_text)
            return redirect('/')
        else:
            return self.render_template('add.html')

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(redis_host='127.0.0.1', redis_port=6379, redis_pass='123'):
    app = Shortly({
        'redis_host': redis_host,
        'redis_port': redis_port,
        'redis_pass': redis_pass
    })
    return app


if __name__ == '__main__':
    port = 9999
    print 'start server on ', port
    app = create_app()
    run_simple(hostname='0.0.0.0', port=port, application=app, use_debugger=1, use_reloader=1)

