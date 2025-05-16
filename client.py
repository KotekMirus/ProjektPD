import requests
import keyring
import pyqrcode
import pyotp
import encryption_management

SERVER_URL = "https://127.0.0.1:5000"

def register(username,password):
    response = requests.post(f"{SERVER_URL}/register",json={"username":username,"password":password},verify=False)
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
    return response.json()['status']

def login(username,password):
    response = requests.post(f"{SERVER_URL}/login",json={"username":username,"password":password},verify=False)
    if 'token' in list(response.json().keys()):
        try:
            keyring.delete_password("Chattersi",username)
        except keyring.errors.PasswordDeleteError:
            pass
        keyring.set_password('Chattersi',username,(response.json())['token'])
    return response.json()['status']

def logout(username):
    try:
        keyring.delete_password("Chattersi",username)
    except keyring.errors.PasswordDeleteError:
        pass

def verify_totp(username,totp_code):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/totp",json={"totp_code":totp_code,"token":token},verify=False)
    if 'token' in list(response.json().keys()):
        try:
            keyring.delete_password("Chattersi",username)
        except keyring.errors.PasswordDeleteError:
            pass
        keyring.set_password('Chattersi',username,(response.json())['token'])
    return response.json()['status']

def invite(username,user):
    token = keyring.get_password('Chattersi',username)
    private_key,public_key = encryption_management.generate_asymmetric_keys()
    encryption_management.save_key(private_key,user,True)
    response = requests.post(f"{SERVER_URL}/invite", json={"user":user,"key":public_key,"token":token},verify=False)
    return response.json()['status']

def reply_to_invitation(username,user,decision):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/decide", json={"user":user,"decision":decision,"token":token},verify=False)
    if 'key' in list(response.json().keys()):
        encryption_management.save_key((response.json())['key'],user,True)
        symmetric_key = encryption_management.generate_symmetric_key()
        encryption_management.save_key(symmetric_key,user,False)
        encrypted_symmetric_key = encryption_management.encrypt_message_asymmetric(encryption_management.get_key(user,True),symmetric_key)
        next_response = requests.post(f"{SERVER_URL}/addkey", json={"user":user,"key":encrypted_symmetric_key,"token":token},verify=False)
        encryption_management.delete_tmp_key(user)
        return next_response.json()['status']
    return response.json()['status']

def get_chat_members(username,room_type):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/getrooms", json={"room_type":room_type,"token":token},verify=False)
    return response.json()['status'],response.json()['users']

def get_room_code(username,user):
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/getcode", json={"user":user,"token":token},verify=False)
    if 'key' in list(response.json().keys()):
        symmetric_key = encryption_management.decrypt_message_asymmetric(encryption_management.get_key(user,True),(response.json())['key'])
        encryption_management.delete_tmp_key(user)
        encryption_management.save_key(symmetric_key,user,False)
    return response.json()['status'],response.json()['room_code']

def send_message(username,room_code,user,message,date):
    token = keyring.get_password('Chattersi',username)
    symmetric_key = encryption_management.get_key(user,False)
    final_message = [encryption_management.encrypt_message_symmetric(symmetric_key,message),date]
    response = requests.post(f"{SERVER_URL}/send", json={"room_code":room_code,"message":final_message,"token":token},verify=False)
    return response.json()['status']

def get_messages(username,room_code,user):
    token = keyring.get_password('Chattersi',username)
    symmetric_key = encryption_management.get_key(user,False)
    response = requests.post(f"{SERVER_URL}/get", json={"room_code":room_code,"token":token},verify=False)
    messages = [[encryption_management.decrypt_message_symmetric(symmetric_key,message),timestamp] for message,timestamp in (response.json())['messages']]
    return response.json()['status'],messages