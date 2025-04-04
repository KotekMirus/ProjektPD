import requests
import keyring
import pyqrcode
import pyotp
import datetime

SERVER_URL = "http://127.0.0.1:5000"

def register(username,password):
    response = requests.post(f"{SERVER_URL}/register",json={"username":username,"password":password})
    if 'token' in list(response.json().keys()):
        try:
            keyring.delete_password("Chattersi",username)
        except keyring.errors.PasswordDeleteError:
            pass
        keyring.set_password('Chattersi',username,(response.json())['token'])
    if 'secret_key' in list(response.json().keys()):
        totp = pyotp.TOTP((response.json())['secret_key'])
        uri = totp.provisioning_uri(name=username,issuer_name='Chattersi')
        qr_code = pyqrcode.create(uri)
        qr_code.png(f"images/{username}_qr_code.png",scale=6)
    return response.json()

def login(username,password):
    response = requests.post(f"{SERVER_URL}/login",json={"username":username,"password":password})
    if 'token' in list(response.json().keys()):
        try:
            keyring.delete_password("Chattersi",username)
        except keyring.errors.PasswordDeleteError:
            pass
        keyring.set_password('Chattersi',username,(response.json())['token'])
    return response.json()

def logout(username):
    try:
        keyring.delete_password("Chattersi",username)
    except keyring.errors.PasswordDeleteError:
        pass

def verify_totp(username,totp_code):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/totp",json={"totp_code":totp_code,"token":token})
    if 'token' in list(response.json().keys()):
        try:
            keyring.delete_password("Chattersi",username)
        except keyring.errors.PasswordDeleteError:
            pass
        keyring.set_password('Chattersi',username,(response.json())['token'])
    return response.json()

def invite(username,user):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/invite", json={"user":user,"token":token})
    return response.json()

def reply_to_invitation(username,user,decision):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/decide", json={"user":user,"decision":decision,"token":token})
    return response.json()

def get_chat_members(username,room_type):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/getrooms", json={"room_type":room_type,"token":token})
    return response.json()

def get_room_code(username,user):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/getcode", json={"user":user,"token":token})
    return response.json()

def send_message(username,room_code,message):
    token = keyring.get_password('Chattersi',username)
    final_message = [message,str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))]
    response = requests.post(f"{SERVER_URL}/send", json={"room_code":room_code,"message":final_message,"token":token})
    return response.json()

def get_messages(username,room_code):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/get", json={"room_code":room_code,"token":token})
    return response.json()