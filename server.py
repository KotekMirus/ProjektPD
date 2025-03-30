import flask
import jwt
import datetime
import random
import user_handling

app = flask.Flask('Czat')
key = open("key.txt", "r")
app.secret_key = key.read()

rooms = {}

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
    
def generate_room_code():
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
            return flask.jsonify({'status':200,'message':message,'token':token})
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
        if token_content is None:
            message = 'Nie można przystąpić do weryfikacji TOTP'
            return flask.jsonify({'status':400,'message':message})
        if token_content.get('mode') == 'totp':
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
        token_content = decode_jwt(token)
        if token_content is None:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})
        if token_content.get('mode') == 'logedin':
            remote_user = data.get('user')
            username = token_content.get('user_id')
            room_code = generate_room_code()
            rooms[room_code] = [username,remote_user]
            message = 'Wysłano zproszenie do '+remote_user
            return flask.jsonify({'status':200,'message':message})
        else:
            message = 'Brak zalogowanego użytkownika'
            return flask.jsonify({'status':400,'message':message})

def run_server():
    app.run()