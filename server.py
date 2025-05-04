import flask
import jwt
import datetime
import random
import json
import os
import user_handling

app = flask.Flask('Chattersi')
key = open("key.txt", "r")
app.secret_key = key.read()

def create_jwt(username,mode,time_version):
    period = None
    if time_version == 0:
        period = datetime.timedelta(hours=6)
    else:
        period = datetime.timedelta(minutes=5)
    payload = {
        "user_id": username,
        "mode": mode,
        "exp": datetime.datetime.now(datetime.timezone.utc) + period
    }
    token = jwt.encode(payload,key.read(),algorithm="HS256")
    return token

def decode_jwt(token):
    try:
        decoded_payload = jwt.decode(token,key.read(),algorithms=["HS256"])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def check_rooms_file_existence():
    if os.path.isdir('data') == False:
        os.mkdir('data')
    if os.path.isfile('data/rooms.json') == False:
        with open('data/rooms.json','w') as file:
            json.dump({}, file, indent = 3)

def get_rooms_codes():
    check_rooms_file_existence()
    rooms = None
    with open('data/rooms.json','r') as file:
        rooms = json.load(file)  
    return list(rooms.keys())
       
def save_room(room_code,members,author):
    check_rooms_file_existence()
    rooms = None
    with open('data/rooms.json','r') as file:
        rooms = json.load(file)
    rooms[room_code] = {'members':members,'author':author,members[0]:[],members[1]:[]}
    with open('data/rooms.json','w') as file:
        json.dump(rooms, file, indent = 3)

def add_key_to_room(room_code,key):
    check_rooms_file_existence()
    rooms = None
    with open('data/rooms.json','r') as file:
        rooms = json.load(file)
    rooms[room_code]['key'] = key
    with open('data/rooms.json','w') as file:
        json.dump(rooms, file, indent = 3)

def get_key_from_room(room_code):
    check_rooms_file_existence()
    rooms = None
    with open('data/rooms.json','r') as file:
        rooms = json.load(file)
    found_key = None
    if 'key' in rooms[room_code]:
        found_key = rooms[room_code]['key']
        del rooms[room_code]['key']
    with open('data/rooms.json','w') as file:
        json.dump(rooms, file, indent = 3)
    return found_key

def get_roommates(room_codes):
    check_rooms_file_existence()
    rooms = None
    with open('data/rooms.json','r') as file:
        rooms = json.load(file)
    members = []
    for code in room_codes:
        members += rooms[code]['members']
    return members

def find_room(user1,user2):
    check_rooms_file_existence()
    rooms = None
    with open('data/rooms.json','r') as file:
        rooms = json.load(file)
    found_code = None
    room_author = None
    for code in list(rooms.keys()):
        if user1 in rooms[code]['members'] and user2 in rooms[code]['members']:
            found_code = code
            room_author = rooms[code]['author']
            break
    users = None
    found_key = None
    with open('data/users.json','r') as file:
        users = json.load(file)
    for code,key in users[user1]['pending_rooms']:
        if code == found_code:
            found_key = key
    return found_code, room_author, found_key

def find_all_user_rooms(username,room_type):
    users = None
    with open('data/users.json','r') as file:
        users = json.load(file)
    roommates_tmp = None
    if room_type == 'chats':
        room_codes = users[username]['rooms']
        roommates_tmp = get_roommates(room_codes)
    elif room_type == 'invitations':
        pending_room_codes = [element[0] for element in users[username]['pending_rooms']]
        roommates_tmp = get_roommates(pending_room_codes)
    else:
        return []
    roommates = [user for user in roommates_tmp if user != username]
    return roommates

def save_sent_message(room_code,author,message):
    check_rooms_file_existence()
    rooms = None
    with open('data/rooms.json','r') as file:
        rooms = json.load(file)
    rooms[room_code][author].append(message)
    with open('data/rooms.json','w') as file:
        json.dump(rooms, file, indent = 3)

def return_all_messages(room_code,receiver):
    check_rooms_file_existence()
    rooms = None
    with open('data/rooms.json','r') as file:
        rooms = json.load(file)
    members = rooms[room_code]['members']
    author = ([member for member in members if member != receiver])[0]
    messages = rooms[room_code][author]
    rooms[room_code][author] = []
    with open('data/rooms.json','w') as file:
        json.dump(rooms, file, indent = 3)
    return messages

def generate_room_code():
    rooms = get_rooms_codes()
    while True:
        code = ''
        for _ in range(6):
            code += str(random.randint(0,9))
        if code not in rooms:
            break
    return code

@app.route('/register',methods=['POST'])
def register():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            message = 'Brak nazwy użytkownika lub hasła'
            return flask.jsonify({'status':400,'message':message})
        if len(username) < 3:
            message = 'Nazwa użytkownika jest zbyt krótka (minimum 3 znaki)'
            return flask.jsonify({'status':400,'message':message})
        if len(username) > 32:
            message = 'Nazwa użytkownika jest zbyt długa (maksimum 32 znaki)'
            return flask.jsonify({'status':400,'message':message})
        for letter in username:
            if letter in ['<','>',':','“','"','/','\\','|','?','*']:
                message = 'Nazwa użytkownika zawiera niedozwolone znaki (< > : “ " / \\ | ? *)'
                return flask.jsonify({'status':400,'message':message})
        if len(password) < 12:
            message = 'Hasło jest za krótkie (minimum 12 znaków)'
            return flask.jsonify({'status':400,'message':message})
        if len(password) > 64:
            message = 'Hasło jest za długie (maksimum 64 znaki)'
            return flask.jsonify({'status':400,'message':message})
        new_user = user_handling.user(username,password)
        if new_user.register():
            token = create_jwt(username,'logedin',0)
            message = 'Poprawnie zarejestrowano użytkownika'
            return flask.jsonify({'status':200,'message':message,'token':token,'secret_key':new_user.secret_key})
        else:
            message = 'Ta nazwa użytkownika jest już zajęta'
            return flask.jsonify({'status':400,'message':message})
        
@app.route('/login',methods=['POST'])
def login():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        username = data.get('username')
        password = data.get('password')
        actual_user = user_handling.user(username,password)
        if actual_user.verify():
            token = create_jwt(username,'totp',1)
            message = 'Prawidłowe dane logowania'
            return flask.jsonify({'status':200,'message':message,'token':token})
        else:
            message = 'Nieprawidłowe dane logowania'
            return flask.jsonify({'status':400,'message':message})
    
@app.route('/totp',methods=['POST'])
def check_totp():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        token = data.get('token')
        token_content = decode_jwt(token)
        mode = None
        try:
            mode = token_content.get('mode')
        except Exception:
            message = 'Nie można przystąpić do weryfikacji TOTP'
            return flask.jsonify({'status':400,'message':message})
        if mode == 'totp':
            totp_code = data.get('totp_code')
            username = token_content.get('user_id')
            actual_user = user_handling.user(username,None)
            if actual_user.verify_totp(totp_code):
                new_token = create_jwt(username,'logedin',0)
                message = 'Weryfikacja TOTP zakończona sukcesem'
                return flask.jsonify({'status':200,'message':message,'token':new_token})
            else:
                message = 'Weryfikacja TOTP zakończona niepowodzeniem'
                return flask.jsonify({'status':400,'message':message})
        else:
            message = 'Nie można przystąpić do weryfikacji TOTP'
            return flask.jsonify({'status':400,'message':message})

@app.route('/invite',methods=['POST'])
def invite():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        token = data.get('token')
        remote_user = data.get('user')
        encryption_key = data.get('key')
        token_content = decode_jwt(token)
        mode = None
        try:
            mode = token_content.get('mode')
        except Exception:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        users = None
        with open('data/users.json','r') as file:
            users = list(json.load(file).keys())
        if remote_user not in users:
            message = 'Podany użytkownik nie istnieje'
            return flask.jsonify({'status':400,'message':message})
        if mode == 'logedin':
            username = token_content.get('user_id')
            user = user_handling.user(username,None)
            accepted,pending = user.get_room_codes()
            if remote_user in get_roommates(accepted+pending):
                message = 'Ten użytkownik został już wcześniej zaproszony'
                return flask.jsonify({'status':400,'message':message})
            else:
                room_code = generate_room_code()
                save_room(room_code,[username,remote_user],username)
                room_creator = user_handling.user(username,None)
                room_creator.add_to_pending_room(room_code,remote_user,encryption_key)
                message = 'Wysłano zproszenie do '+remote_user
                return flask.jsonify({'status':200,'message':message})
        else:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})

@app.route('/decide',methods=['POST'])
def reply_to_invitation():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        token = data.get('token')
        remote_user = data.get('user')
        token_content = decode_jwt(token)
        mode = None
        try:
            mode = token_content.get('mode')
        except Exception:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        users = None
        users_names = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        users_names = list(users.keys())
        if remote_user not in users_names:
            message = 'Podany użytkownik nie istnieje'
            return flask.jsonify({'status':400,'message':message})
        if mode == 'logedin':
            username = token_content.get('user_id')
            code,author,encryption_key = find_room(username,remote_user)
            if code is not None and author != username:
                decision = data.get('decision')
                if decision == 'accept':
                    users[username]['pending_rooms'].remove([code,encryption_key])
                    users[username]['rooms'].append(code)
                    users[remote_user]['pending_rooms'].remove([code,encryption_key])
                    users[remote_user]['rooms'].append(code)
                    with open('data/users.json','w') as file:
                        json.dump(users, file, indent = 3)
                    message = 'Poprawnie zaakceptowano rozmowę między '+username+' a '+remote_user
                    return flask.jsonify({'status':200,'message':message,'key':encryption_key})
                elif decision == 'decline':
                    users[username]['pending_rooms'].remove([code,encryption_key])
                    users[remote_user]['pending_rooms'].remove([code,encryption_key])
                    with open('data/users.json','w') as file:
                        json.dump(users, file, indent = 3)
                    rooms = None
                    with open('data/rooms.json','r') as file:
                        rooms = json.load(file)
                    rooms.pop(code)
                    with open('data/rooms.json','w') as file:
                        json.dump(rooms, file, indent = 3)
                    message = 'Poprawnie odrzucono rozmowę między '+username+' a '+remote_user
                    return flask.jsonify({'status':200,'message':message})
                else:
                    message = 'Nieprawidłowa decyzja'
                    return flask.jsonify({'status':400,'message':message})
            else:
                message = 'Podany użytkownik nie został wcześniej zaproszony lub brak uprawnień do akceptacji tego zaproszenia'
                return flask.jsonify({'status':400,'message':message})
        else:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        
@app.route('/addkey',methods=['POST'])
def add_symmetric_key_to_room():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        token = data.get('token')
        remote_user = data.get('user')
        symmetric_key = data.get('key')
        token_content = decode_jwt(token)
        mode = None
        try:
            mode = token_content.get('mode')
        except Exception:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        users = None
        users_names = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        users_names = list(users.keys())
        if remote_user not in users_names:
            message = 'Podany użytkownik nie istnieje'
            return flask.jsonify({'status':400,'message':message})
        if mode == 'logedin':
            username = token_content.get('user_id')
            code,author,encryption_key = find_room(username,remote_user)
            if code is not None and author != username and remote_user in find_all_user_rooms(username,'chats'):
                add_key_to_room(code,symmetric_key)
                message = 'Poprawnie wysłano klucz symetryczny'
                return flask.jsonify({'status':200,'message':message})
            else:
                message = 'Nie można dodać klucza symetrycznego do tej rozmowy'
                return flask.jsonify({'status':400,'message':message})
        else:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        
@app.route('/getrooms',methods=['POST'])
def get_rooms():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        token = data.get('token')
        token_content = decode_jwt(token)
        mode = None
        try:
            mode = token_content.get('mode')
        except Exception:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        if mode == 'logedin':
            username = token_content.get('user_id')
            room_type = data.get('room_type')
            users = find_all_user_rooms(username,room_type)
            message = 'Zwrócono członków danych pokoi'
            return flask.jsonify({'status':200,'message':message,'users':users})
        else:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})

@app.route('/getcode',methods=['POST'])
def get_room_code():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        token = data.get('token')
        token_content = decode_jwt(token)
        mode = None
        try:
            mode = token_content.get('mode')
        except Exception:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        if mode == 'logedin':
            username = token_content.get('user_id')
            remote_user = data.get('user')
            room_code,author,encryption_key = find_room(username,remote_user)
            if room_code is not None:
                message = 'Poprawnie znaleziono kod rozmowy z podanym użytkownikiem'
                if username == author:
                    symmetric_key = get_key_from_room(room_code)
                    if symmetric_key != None:
                        return flask.jsonify({'status':200,'message':message,'room_code':room_code,'key':symmetric_key})
                return flask.jsonify({'status':200,'message':message,'room_code':room_code})
            else:
                message = 'Brak rozmowy z podanym użytkownikiem'
                return flask.jsonify({'status':400,'message':message})
        else:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})

@app.route('/send',methods=['POST'])
def send_message():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        token = data.get('token')
        token_content = decode_jwt(token)
        mode = None
        try:
            mode = token_content.get('mode')
        except Exception:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        if mode == 'logedin':
            username = token_content.get('user_id')
            room_code = data.get('room_code')
            user = user_handling.user(username,None)
            accepted,pending = user.get_room_codes()
            if room_code in accepted:
                sent_message = data.get('message')
                save_sent_message(room_code,username,sent_message)
                message = 'Poprawnie wysłano wiadomość'
                return flask.jsonify({'status':200,'message':message})
            else:
                message = 'Nie można wysłać wiadomości do tego użytkownika'
                return flask.jsonify({'status':400,'message':message})
        else:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})

@app.route('/get',methods=['POST'])
def get_messages():
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        token = data.get('token')
        token_content = decode_jwt(token)
        mode = None
        try:
            mode = token_content.get('mode')
        except Exception:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        if mode == 'logedin':
            username = token_content.get('user_id')
            room_code = data.get('room_code')
            user = user_handling.user(username,None)
            accepted,pending = user.get_room_codes()
            if room_code in accepted:
                messages = return_all_messages(room_code,username)
                message = 'Poprawnie odświeżono stan otrzymanych wiadomości'
                return flask.jsonify({'status':200,'message':message,'messages':messages})
            else:
                message = 'Nie można pobrać tych wiadomości'
                return flask.jsonify({'status':400,'message':message})
        else:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})

def run_server():
    app.run()