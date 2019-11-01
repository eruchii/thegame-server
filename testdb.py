from db import get_session, user_exists, add_user

session = get_session()

print(add_user(session,"pepe","thefrog","thefrog"))
print(user_exists(session,"monkaS"))
print(user_exists(session,"pepe"))
