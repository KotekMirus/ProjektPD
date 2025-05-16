import pytest
import subprocess
import time
import requests
import keyring
import pyotp
import os

SERVER_URL = "https://127.0.0.1:5000"

sample_user_1 = {"username":"Mimir","password":"TestPassword123#"}
sample_user_2 = {"username":"Loki","password":"AnotherPassword321!"}
incorrect_user_1 = {"username":"X","password":"G00dPassword479@"}
incorrect_user_2 = {"username":"Artemis","password":"weak"}

@pytest.fixture(scope="module")
def start_server():
    if os.path.isfile('data/users.json'):
        os.remove('data/users.json')
    if os.path.isfile('data/rooms.json'):
        os.remove('data/rooms.json')
    process = subprocess.Popen(["python","main.py","server"])
    time.sleep(7)
    yield
    process.terminate()
    if os.path.isfile('data/users.json'):
        os.remove('data/users.json')
    if os.path.isfile('data/rooms.json'):
        os.remove('data/rooms.json')

def test_register(start_server):
    response = requests.post(f"{SERVER_URL}/register",json={"username":sample_user_1["username"],"password":sample_user_1["password"]},verify=False)
    assert response.json()['status'] == 200
    keyring.set_password('Chattersi',sample_user_1["username"],(response.json())['token'])
    sample_user_1["secret_key"] = response.json()['secret_key']
    response = requests.post(f"{SERVER_URL}/register",json={"username":sample_user_2["username"],"password":sample_user_2["password"]},verify=False)
    assert response.json()['status'] == 200
    keyring.set_password('Chattersi',sample_user_2["username"],(response.json())['token'])
    sample_user_2["secret_key"] = response.json()['secret_key']
    response = requests.post(f"{SERVER_URL}/register",json={"username":sample_user_2["username"],"password":sample_user_2["password"]},verify=False)
    assert response.json()['status'] == 400
    response = requests.post(f"{SERVER_URL}/register",json={"username":incorrect_user_1["username"],"password":incorrect_user_1["password"]},verify=False)
    assert response.json()['status'] == 400
    response = requests.post(f"{SERVER_URL}/register",json={"username":incorrect_user_2["username"],"password":incorrect_user_2["password"]},verify=False)
    assert response.json()['status'] == 400
    keyring.delete_password("Chattersi",sample_user_1["username"])
    keyring.delete_password("Chattersi",sample_user_2["username"])

def test_login(start_server):
    response = requests.post(f"{SERVER_URL}/login",json={"username":sample_user_1["username"],"password":sample_user_1["password"]},verify=False)
    assert response.json()['status'] == 200
    keyring.set_password('Chattersi',sample_user_1["username"],(response.json())['token'])
    response = requests.post(f"{SERVER_URL}/login",json={"username":sample_user_2["username"],"password":sample_user_2["password"]},verify=False)
    assert response.json()['status'] == 200
    keyring.set_password('Chattersi',sample_user_2["username"],(response.json())['token'])
    response = requests.post(f"{SERVER_URL}/login",json={"username":incorrect_user_1["username"],"password":incorrect_user_1["password"]},verify=False)
    assert response.json()['status'] == 400
    response = requests.post(f"{SERVER_URL}/login",json={"username":sample_user_1["username"],"password":incorrect_user_1["password"]},verify=False)
    assert response.json()['status'] == 400

def test_check_totp(start_server):
    response = requests.post(f"{SERVER_URL}/totp",json={"totp_code":'0',"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400
    totp1 = pyotp.TOTP(sample_user_1['secret_key'])
    response = requests.post(f"{SERVER_URL}/totp",json={"totp_code":totp1.now(),"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 200
    keyring.delete_password("Chattersi",sample_user_1["username"])
    keyring.set_password('Chattersi',sample_user_1["username"],(response.json())['token'])
    totp2 = pyotp.TOTP(sample_user_2['secret_key'])
    response = requests.post(f"{SERVER_URL}/totp",json={"totp_code":totp2.now(),"token":keyring.get_password('Chattersi',sample_user_2["username"])},verify=False)
    assert response.json()['status'] == 200
    keyring.delete_password("Chattersi",sample_user_2["username"])
    keyring.set_password('Chattersi',sample_user_2["username"],(response.json())['token'])
    response = requests.post(f"{SERVER_URL}/totp",json={"totp_code":totp1.now(),"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400

def test_invite(start_server):
    sample_user_1["tmp_keys"] = {sample_user_2["username"]:"123"}
    response = requests.post(f"{SERVER_URL}/invite", json={"user":sample_user_2["username"],"key":sample_user_1["tmp_keys"][sample_user_2["username"]],"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 200
    response = requests.post(f"{SERVER_URL}/invite", json={"user":sample_user_2["username"],"key":sample_user_1["tmp_keys"][sample_user_2["username"]],"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400
    response = requests.post(f"{SERVER_URL}/invite", json={"user":incorrect_user_1["username"],"key":"456","token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400
    response = requests.post(f"{SERVER_URL}/invite", json={"user":sample_user_1["username"],"key":"456","token":keyring.get_password('Chattersi',sample_user_2["username"])},verify=False)
    assert response.json()['status'] == 400
    response = requests.post(f"{SERVER_URL}/invite", json={"user":sample_user_2["username"],"key":"456","token":keyring.get_password('Chattersi',incorrect_user_1["username"])},verify=False)
    assert response.json()['status'] == 400

def test_reply_to_invitation(start_server):
    response = requests.post(f"{SERVER_URL}/decide", json={"user":sample_user_2["username"],"decision":"accept","token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400
    response = requests.post(f"{SERVER_URL}/decide", json={"user":sample_user_1["username"],"decision":"accept","token":keyring.get_password('Chattersi',sample_user_2["username"])},verify=False)
    assert response.json()['status'] == 200
    assert response.json()['key'] == sample_user_1["tmp_keys"][sample_user_2["username"]]
    response = requests.post(f"{SERVER_URL}/decide", json={"user":incorrect_user_1["username"],"decision":"accept","token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400
    response = requests.post(f"{SERVER_URL}/decide", json={"user":sample_user_1["username"],"decision":"accept","token":keyring.get_password('Chattersi',incorrect_user_1["username"])},verify=False)
    assert response.json()['status'] == 400

def test_add_symmetric_key(start_server):
    sample_user_2["keys"] = {sample_user_1["username"]:"321"}
    response = requests.post(f"{SERVER_URL}/addkey", json={"user":sample_user_2["username"],"key":"654","token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400
    response = requests.post(f"{SERVER_URL}/addkey", json={"user":sample_user_1["username"],"key":sample_user_2["keys"][sample_user_1["username"]],"token":keyring.get_password('Chattersi',sample_user_2["username"])},verify=False)
    assert response.json()['status'] == 200
    response = requests.post(f"{SERVER_URL}/addkey", json={"user":sample_user_2["username"],"key":"654","token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400

def test_get_rooms(start_server):
    response = requests.post(f"{SERVER_URL}/getrooms", json={"room_type":'chats',"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 200
    assert sample_user_2["username"] in response.json()['users']
    response = requests.post(f"{SERVER_URL}/getrooms", json={"room_type":'invitations',"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 200
    response = requests.post(f"{SERVER_URL}/getrooms", json={"room_type":'x',"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 200
    assert not response.json()['users']

def test_get_room_code(start_server):
    response = requests.post(f"{SERVER_URL}/getcode", json={"user":sample_user_1["username"],"token":keyring.get_password('Chattersi',sample_user_2["username"])},verify=False)
    assert response.json()['status'] == 200
    assert 'key' not in list(response.json().keys())
    sample_user_1['room_code'] = response.json()['room_code']
    response = requests.post(f"{SERVER_URL}/getcode", json={"user":sample_user_2["username"],"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 200
    assert 'key' in list(response.json().keys())
    response = requests.post(f"{SERVER_URL}/getcode", json={"user":sample_user_2["username"],"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 200
    assert 'key' not in list(response.json().keys())
    response = requests.post(f"{SERVER_URL}/getcode", json={"user":'x',"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400

def test_send_message(start_server):
    response = requests.post(f"{SERVER_URL}/send", json={"room_code":sample_user_1['room_code'],"message":['Cześć','04-05-2025 12:26:17'],"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 200
    response = requests.post(f"{SERVER_URL}/send", json={"room_code":sample_user_1['room_code'],"message":['Hejo','04-05-2025 12:31:58'],"token":keyring.get_password('Chattersi',sample_user_2["username"])},verify=False)
    assert response.json()['status'] == 200
    response = requests.post(f"{SERVER_URL}/send", json={"room_code":'0',"message":['Co?','04-05-2025 18:29:04'],"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400

def test_get_message(start_server):
    response = requests.post(f"{SERVER_URL}/get", json={"room_code":sample_user_1['room_code'],"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 200
    assert [['Hejo','04-05-2025 12:31:58']] == response.json()['messages']
    response = requests.post(f"{SERVER_URL}/get", json={"room_code":sample_user_1['room_code'],"token":keyring.get_password('Chattersi',sample_user_2["username"])},verify=False)
    assert response.json()['status'] == 200
    assert [['Cześć','04-05-2025 12:26:17']] == response.json()['messages']
    response = requests.post(f"{SERVER_URL}/get", json={"room_code":'0',"token":keyring.get_password('Chattersi',sample_user_1["username"])},verify=False)
    assert response.json()['status'] == 400

