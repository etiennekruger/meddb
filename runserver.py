from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple

from backend import app as backend_app
from frontend import app as frontend_app

application = DispatcherMiddleware(
    frontend_app,
    {
        '/api': backend_app,
    }
)

if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)
