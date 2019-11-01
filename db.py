from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models import User, Base
import hashlib

def encrypt_string(hash_string):
	sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
	return sha_signature


def init_db():
	engine = create_engine('sqlite:///thegame.db')
	Base.metadata.create_all(engine)

def add_user(session, username, password, check_password):
	user = session.query(User).filter_by(username=username).first()
	if user:
		return (False, 'User already exists')

	if len(password) < 1:
		return (False, 'Password too short')

	if password != check_password:
		return (False, 'Passwords do not match')

	hashed = encrypt_string(password)
	token = encrypt_string(username+hashed)
	new_user = User(username=username,
					password=hashed,
					token=token)

	session.add(new_user)
	session.commit()

	return (True, token)


def user_exists(session, username):
	user = session.query(User).filter_by(username=username).first()

	if not user:
		return (False, 'User does not exist')

	return (True, 'User exists')


def check_user(session, username, password):
	user = session.query(User).filter_by(username=username).first()

	if not user:
		return (False, 'User does not exist')

	if encrypt_string(password) == user.password:
		return (True, user.token)
	else:
		return (False, 'Incorrect password')

def get_token(session, username):
	user = session.query(User).filter_by(username=username).first()
	if not user:
		return (False, 'User does not exist')
	return (True, user.token)

def find_token(session, token):
	user = session.query(User).filter_by(token=token).first()
	if not user:
		return (False, 'Token does not exist')
	return (True, user.username)

def get_session():
	engine = create_engine('sqlite:///thegame.db')
	Base.metadata.bind = engine
	if not (engine.dialect.has_table(engine, 'users')):
		init_db()
	DBSession = sessionmaker()
	DBSession.bind = engine
	return DBSession()
