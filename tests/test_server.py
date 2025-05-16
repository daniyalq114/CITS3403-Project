from app import create_app
from config import TestConfig

def run_test_server():
    app = create_app(TestConfig)
    app.run(port=5000, use_reloader=False)

if __name__ == '__main__':
    run_test_server()