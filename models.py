from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	username = Column(String, nullable = False, primary_key=True)
	password = Column(String, nullable = False)
	token = Column(String, nullable = False)
	def __repr__(self):
		return "<User(username='%s', password='%s', token='%s')>" % (self.username, self.password, self.token)