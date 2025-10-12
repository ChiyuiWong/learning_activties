"""Start the backend Flask app using TestConfig for tests (uses mongomock).

This script writes its PID to `test_server.pid` so the test runner can stop it.
"""
import os
import sys
from app import create_app
from app.config.config import TestConfig


def main():
    # Ensure working dir is backend
    os.chdir(os.path.dirname(__file__))

    app = create_app(TestConfig)

    # Write PID to file so callers can terminate the server
    pid = os.getpid()
    with open('test_server.pid', 'w') as f:
        f.write(str(pid))

    # Run the app (do not use debug reloader)
    app.run(host='127.0.0.1', port=5000, debug=False)


if __name__ == '__main__':
    main()
