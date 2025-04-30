from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64
import json
import os

def generate_asymmetric_keys():
    private_key = rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public_key = private_key.public_key()
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    pem_private_str = pem_private.decode('utf-8')
    pem_public_str = pem_public.decode('utf-8')
    return pem_private_str,pem_public_str

def generate_symmetric_key():
    key = Fernet.generate_key()
    return key.decode()

def check_structure_existence():
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isfile('data/keys.json'):
        with open('data/keys.json','w') as file:
            json.dump({}, file, indent = 3)
    if not os.path.isfile('data/tmp_keys.json'):
        with open('data/tmp_keys.json','w') as file:
            json.dump({}, file, indent = 3)

def save_key(key,user,tmp):
    check_structure_existence()
    filename = None
    if tmp:
        filename = 'data/tmp_keys.json'
    else:
        filename = 'data/keys.json'
    all_keys = None
    with open(filename,'r') as file:
        all_keys = json.load(file)
    all_keys[user] = key
    with open(filename,'w') as file:
        json.dump(all_keys, file, indent = 3)

def delete_tmp_key(user):
    check_structure_existence()
    all_keys = None
    with open('data/tmp_keys.json','r') as file:
        all_keys = json.load(file)
    if user in all_keys.keys():
        all_keys.pop(user)
        with open('data/tmp_keys.json','w') as file:
            json.dump(all_keys, file, indent = 3)

def encrypt_message_asymmetric(key,message):
    public_key = serialization.load_pem_public_key(key.encode())
    encrypted = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None))
    return base64.b64encode(encrypted).decode()

def encrypt_message_symmetric(key,message):
    f = Fernet(key.encode())
    encrypted = f.encrypt(message.encode())
    return encrypted.decode()

def decrypt_message_asymmetric(key,encrypted_message):
    private_key = serialization.load_pem_private_key(key.encode(), password=None)
    decrypted = private_key.decrypt(
        base64.b64decode(encrypted_message),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None))
    return decrypted.decode()

def decrypt_message_symmetric(key,encrypted_message):
    f = Fernet(key.encode())
    decrypted = f.decrypt(encrypted_message.encode())
    return decrypted.decode()