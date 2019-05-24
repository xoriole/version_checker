import json

from flask import Flask
from flask_login import LoginManager
from pony.flask import Pony

from six.moves.urllib.request import urlopen

from config import config
from models import db


app = Flask(__name__)
app.config.update(config)

app.config['release_url'] = "https://api.github.com/repos/tribler/tribler/releases/latest"
app.config['release_info'] = json.loads(urlopen(app.config['release_url']).read())

Pony(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.User.get(id=user_id)
