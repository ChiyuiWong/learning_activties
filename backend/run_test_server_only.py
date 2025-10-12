from werkzeug.serving import make_server
from app import create_app
from app.config.config import TestConfig

if __name__ == '__main__':
    app = create_app(TestConfig)
    srv = make_server('127.0.0.1', 5000, app)
    print('Test server starting on http://127.0.0.1:5000')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()
        print('Server stopped')
