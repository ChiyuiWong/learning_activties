import threading
import time
import requests
import sys

from werkzeug.serving import make_server
from app import create_app
from app.config.config import TestConfig


class ServerThread(threading.Thread):
    def __init__(self, app, host='127.0.0.1', port=5000):
        threading.Thread.__init__(self)
        self.srv = make_server(host, port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def wait_ready(url, timeout=10.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def main():
    app = create_app(TestConfig)

    server = ServerThread(app)
    server.start()

    ready = wait_ready('http://127.0.0.1:5000/api/health', timeout=10.0)
    if not ready:
        print('Server did not become ready in time', file=sys.stderr)
        server.shutdown()
        sys.exit(2)

    print('Server ready; running pytest...')

    # Run pytest programmatically
    import pytest

    # Allow passing extra pytest args through the PYTEST_ARGS environment variable
    import os
    extra = os.environ.get('PYTEST_ARGS')
    base_args = ['-vv', '-r', 'a']
    if extra:
        base_args.extend(extra.split())
    # Run pytest with verbose output and show all reasons for failures
    rc = pytest.main(base_args)

    print('pytest finished with rc=', rc)

    server.shutdown()
    server.join()

    sys.exit(rc)


if __name__ == '__main__':
    main()
