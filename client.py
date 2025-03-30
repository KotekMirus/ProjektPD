import requests
import os

SERVER_URL = "http://127.0.0.1:5000"

def register(username,password):
    response = requests.post(f"{SERVER_URL}/register",json={"username":username,"password":password})
    if 'token' in list(response.json().keys()):
        with open("token.txt", "w") as file:
            file.write((response.json())['token'])
    return response.json()

def login(username,password):
    response = requests.post(f"{SERVER_URL}/login",json={"username":username,"password":password})
    if 'token' in list(response.json().keys()):
        with open("token.txt", "w") as file:
            file.write((response.json())['token'])
    return response.json()

def verify_totp(totp_code):
    token = None
    if os.path.isfile("token.txt"):
        with open("token.txt", "r") as file:
            token = file.read()
    response = requests.post(f"{SERVER_URL}/totp",json={"totp_code":totp_code,"token":token})
    return response.json()

def invite(user):
    token = None
    if os.path.isfile("token.txt"):
        with open("token.txt", "r") as file:
            token = file.read()
    response = requests.post(f"{SERVER_URL}/invite", json={"user":user,"token":token})
    return response.json()