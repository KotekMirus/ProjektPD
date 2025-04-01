import keyring.errors
import requests
import keyring

SERVER_URL = "http://127.0.0.1:5000"

def register(username,password):
    response = requests.post(f"{SERVER_URL}/register",json={"username":username,"password":password})
    if 'token' in list(response.json().keys()):
        try:
            keyring.delete_password("Chattersi",username)
        except keyring.errors.PasswordDeleteError:
            pass
        keyring.set_password('Chattersi',username,(response.json())['token'])
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