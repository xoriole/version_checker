from pony.orm import Database, Required, Optional
from flask_login import UserMixin
from datetime import datetime

db = Database()


class User(db.Entity, UserMixin):
    login = Required(str, unique=True)
    password = Required(str)
    last_login = Optional(datetime)


class VersionCheck(db.Entity):
    _table_ = 'VersionCheck'

    node = Optional(int, index=True)
    ip = Required(str, 16, index=True)
    version = Required(str, 16, index=True)
    os = Optional(str, 16, index=True)
    timestamp = Optional(datetime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.identifier,
            'ip': self.ip,
            'version': self.version,
            'timestamp': self.timestamp
        }
