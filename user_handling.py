import json
import os
import bcrypt
import pyotp

class user:
    def __init__(self,username,password):
        self.username = username
        self.password = password
    def register(self):
        self.check_structure_existence()
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        if self.username in list(users.keys()):
            return False
        else:
            self.secret_key = pyotp.random_base32()
            self.save()
            return True
    def check_structure_existence(self):
        if os.path.isdir('data') == False:
            os.mkdir('data')
        if os.path.isfile('data/users.json') == False:
            with open('data/users.json','w') as file:
                json.dump({}, file, indent = 3)
    def save(self):
        self.check_structure_existence()
        hash_password = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode()
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        users[self.username] = {"hash_password":hash_password,"secret_key":self.secret_key,"rooms":[],"pending_rooms":[]}
        with open('data/users.json','w') as file:
            json.dump(users, file, indent = 3)
    def verify(self):
        self.check_structure_existence()
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        if self.username in list(users.keys()):
            found_user = users[self.username]
            check_password_result = bcrypt.checkpw(self.password.encode(),found_user['hash_password'].encode())
            return check_password_result
        else:
            return False
    def verify_totp(self,totp_code):
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        user_secret_key = pyotp.TOTP(users[self.username]["secret_key"])
        if user_secret_key.verify(totp_code,valid_window=1):
            return True
        else:
            return False
    def add_to_pending_room(self,room_code,remote_user):
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        users[self.username]['pending_rooms'].append(room_code)
        users[remote_user]['pending_rooms'].append(room_code)
        with open('data/users.json','w') as file:
            json.dump(users, file, indent = 3)
    def get_room_codes(self):
        self.check_structure_existence()
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        accepted = users[self.username]['rooms']
        pending = users[self.username]['pending_rooms']
        all_room_codes = accepted + pending
        return all_room_codes