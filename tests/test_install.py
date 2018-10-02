import shutil
import time
import sys
import pytest
import threading
import runpy

import flask
import requests


@pytest.fixture
def app():

    def create_app(app_file):
        app_file = runpy.run_path(app_file)
        app = app_file['app']

        @app.server.route('/stop')
        def _stop_server():
            stopper = flask.request.environ['werkzeug.server.shutdown']
            stopper()
            return 'stop'

        def run():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True
            app.run_server(debug=False, port=8050, threaded=True)

        t = threading.Thread(target=run)
        t.daemon = True
        t.start()
        time.sleep(3)

        return app

    yield create_app

    # Stop the server in teardown
    requests.get('http://localhost:8050/stop')


def test_install(cookies, app, selenium):
    results = cookies.bake(extra_context={
        'project_name': 'Test Component',
        'author_name': 'test',
        'author_email': 'test',
        # 'install_dependencies': False
    })

    sys.path.insert(0, str(results.project))

    app(str(results.project.join('usage.py')))

    selenium.get('http://localhost:8050')
    time.sleep(1)

    shutil.rmtree('\\\\?\\' + str(results.project.join('node_modules')))
