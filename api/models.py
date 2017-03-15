
import datetime
import jwt
from api import db, app, bcrypt
import enum
import json


# A base model for other database tables to inherit
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())
    deleted = db.Column(db.Boolean, default=False)

    def serialize(self):
        my_keys = self.__dict__.keys()
        return_dict = {}
        for k in my_keys:
            if k.startswith('_'):
                continue
            value = self.__dict__.get(k)
            if hasattr(value, 'serialize'):
                value = value.serialize()
            return_dict[k] = value
        return return_dict


class ChangeRequest(Base):

    class StateOptions(enum.Enum):
        open = 'open'
        closed = 'closed'
        completed = 'completed'

    __tablename__ = 'change_request'
    summary = db.Column(db.String(255))
    requestor = db.Column(db.String(255))
    application = db.Column(db.String(255))
    source_location = db.Column(db.String(255))
    destination_location = db.Column(db.String(255))
    action = db.Column(db.String(255))
    status = db.Column(db.Enum(StateOptions), default=StateOptions.open)

    def __init__(self, **kwargs):
        self.summary = kwargs.get('summary')
        self.requestor = kwargs.get('requestor')
        self.application = kwargs.get('application')
        self.source_location = kwargs.get('source_location')
        self.destination_location = kwargs.get('destination_location')
        self.action = kwargs.get('action')


class Device(Base):

    class DriverOptions(enum.Enum):
        juniper_srx = 'juniper_srx'
        palo_alto_panorama = 'palo_alto_panorama'

    __tablename__ = 'device'
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    apikey = db.Column(db.String(255), default=None)
    hostname = db.Column(db.String(255))
    driver = db.Column(db.Enum(DriverOptions))

    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.apikey = kwargs.get('apikey')
        self.hostname = kwargs.get('hostname')
        self.driver = kwargs.get('driver')

#added
class Address(Base):

    class TypeOptions(enum.Enum):
        ipv4 = 'ipv4'
        dns = 'dns'
        ipv4_range = 'range'

    __tablename__ = 'service'
    address_type = db.Column(db.Enum(TypeOptions))
    comments = db.Column(db.String(255), default=None)
    value = db.Column(db.String(255))
    hostname = db.Column(db.String(255), default=None)

def __init__(self, **kwargs):
    self.address_type = kwargs.get('address_type')
    self.comments = kwargs.get('comments')
    self.value = kwargs.get('value')
    self.hostname = kwargs.get('hostname')


class Service(Base):
    
    class TypeOptions(enum.Enum):
        layer4 = 'layer4'
        layer7 = 'layer7'

    __tablename__ = 'address'
    type = db.Column(db.Enum(TypeOptions))
    layer4_protocol = db.Column(db.String(255))
    layer4_port = db.Column(db.String(255))
    layer7_value = db.Column(db.String(255))
    comments = db.Column(db.String(255), default=None)

    def __init__(self, **kwargs):
        self.type = kwargs.get('type')
        self.layer4_protocol = kwargs.get('layer4_protocol')
        self.layer4_port = kwargs.get('layer4_port')
        self.layer7_value = kwargs.get('layer7_value')
        self.comments = kwargs.get('comments')

#end added
class User(Base):
    """ User Model for storing user related details """
    __tablename__ = "user"

    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.admin = admin

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class BlacklistToken(Base):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_token'

    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
