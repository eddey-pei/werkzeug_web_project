# coding=utf-8
from werkzeug.wrappers import Request, Response
from werkzeug.utils import escape
from werkzeug.serving import run_simple
from werkzeug.formparser import parse_form_data


@Request.application
def high_hello_world(request):
    result = ['<title>Greeter</title>']
    if request.method == 'POST':
        result.append(
            '<h1>Hello %s!</h1>' % escape(request.form['name'])
        )
    result.append('''
    <form action="" method="post">
    Name: <input type="text" size="20" name="name">
    <input type="submit">
    </form>
    ''')
    return Response(''.join(result), mimetype='text/html')



def low_hello_world(environ, start_response):
    result = ['<title>Greeter</title>']
    if environ['REQUEST_METHOD'] == 'POST':
        form = parse_form_data(environ)[1]
        result.append('<h1>Hello %s!' % escape(form['name']))
    result.append('''
        <form action="" method="post">
        Name: <input type="text" size="20" name="name">
        <input type="submit">
        </form>
        ''')
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return [''.join([bytes(i) for i in result])]    #TODO 中文提交 UnicodeEncodeError  原文[''.join(result)]  AssertionError: applications must write bytes


if __name__ == '__main__':
    # run_simple(hostname='0.0.0.0', port=8888, application=high_hello_world, use_debugger=True, use_reloader=True)
    run_simple(hostname='0.0.0.0', port=8888, application=low_hello_world, use_debugger=True, use_reloader=True)