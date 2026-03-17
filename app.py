import os
from app import create_app
from config import config

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[env])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)