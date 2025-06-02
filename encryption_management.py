"""
Moduł zawierający funkcje odpowiedzialne za generowanie klucza symetrycznego, kluczy asymetrycznych, zapisywanie ich lokalnie
na urządzeniu użytkownika w odpowiednim miejscu oraz szyfrowanie i deszyfrowanie wiadomości z ich pomocą.
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64
import json
import os

def generate_asymmetric_keys():
    """
    Generuje klucz prywatny oraz z jego pomocą tworzy klucz publiczny (algorytm RSA). Klucze zostają przekształcone do postaci
    stringów i zwrócone przez funkcję.

    :return: Para kluczy asymetrycznych (RSA) w formie stringów.
    """
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
    """
    Generuje klucz symetryczny (moduł Fernet). Funkcja zwraca go w postaci stringa.

    :return: Klucz symetryczny w formie stringa.
    """
    key = Fernet.generate_key()
    return key.decode()

def check_structure_existence():
    """
    Sprawdza czy istnieje folder data. Jeśli nie istnieje to go tworzy. Sprawdza czy w folderze data znajdują się pliki keys.json
    oraz tmp_keys.json. Jeśli nie to je tworzy.
    """
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isfile('data/keys.json'):
        with open('data/keys.json','w') as file:
            json.dump({}, file, indent = 3)
    if not os.path.isfile('data/tmp_keys.json'):
        with open('data/tmp_keys.json','w') as file:
            json.dump({}, file, indent = 3)

def save_key(key,user,tmp):
    """
    W zależności od tego czy jako argument tmp przekazano True czy False, zapisuje przekazany klucz przypisany do odpowiedniego
    użytkownika w pliku tmp_keys.json lub keys.json. Z założenia klucze asymetryczne są zapisywane w tmp_keys.json, a symetryczne
    w keys.json.

    :param key: Klucz (asymetryczny lub symetryczny).
    :param user: Użytkownik, będący częścią rozmowy, z którą skojarzony jest klucz.
    :param tmp: Wartość True dla zapisu do pliku tmp_keys.json lub False dla zapisu w pliku keys.json.
    """
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

def get_key(user,tmp):
    """
    W zależności od tego czy jako argument tmp przekazano True czy False, zwraca klucz z pliku tmp_keys.json lub keys.json
    skojarzony ze wskazanym użytkownikiem.

    :param user: Użytkownik, będący częścią rozmowy, z którą skojarzony jest klucz.
    :param tmp: Wartość True dla odczytu z pliku tmp_keys.json lub False dla odczytu z pliku keys.json.
    :return: Klucz (asymetryczny lub symetryczny).
    """
    check_structure_existence()
    filename = None
    if tmp:
        filename = 'data/tmp_keys.json'
    else:
        filename = 'data/keys.json'
    all_keys = None
    with open(filename,'r') as file:
        all_keys = json.load(file)
    found_key = all_keys[user]
    return found_key

def delete_tmp_key(user):
    """
    Usuwa tymczasowy klucz asymetryczny z pliku tmp_keys.json dla wskazanego użytkownika.

    :param user: Użytkownik, będący częścią rozmowy, z którą skojarzony jest klucz.
    """
    check_structure_existence()
    all_keys = None
    with open('data/tmp_keys.json','r') as file:
        all_keys = json.load(file)
    if user in all_keys.keys():
        all_keys.pop(user)
        with open('data/tmp_keys.json','w') as file:
            json.dump(all_keys, file, indent = 3)

def encrypt_message_asymmetric(key,message):
    """
    Szyfruje przekazaną wiadomość asymetrycznie z pomocą klucza publicznego i zwraca szyfrogram w postaci stringa.

    :param key: Klucz publiczny.
    :param message: Wiadomość (z założenia jest nią klucz symetryczny).
    :return: Zaszyfrowana asymetrycznie wiadomość.
    """
    public_key = serialization.load_pem_public_key(key.encode())
    encrypted = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None))
    return base64.b64encode(encrypted).decode()

def encrypt_message_symmetric(key,message):
    """
    Szyfruje przekazaną wiadomość symetrycznie z pomocą klucza symetrycznego i zwraca szyfrogram w postaci stringa.

    :param key: Klucz symetryczny.
    :param message: Wiadomość (z założenia dowolona wiadomość wchodząca w skład rozmowy).
    :return: Zaszyfrowana symetrycznie wiadomość.
    """
    f = Fernet(key.encode())
    encrypted = f.encrypt(message.encode())
    return encrypted.decode()

def decrypt_message_asymmetric(key,encrypted_message):
    """
    Odszyfrowuje przekazaną wiadomość z pomocą przekazanego klucza i zwraca tekst jawny.

    :param key: Klucz prywatny.
    :param encrypted_message: Zaszyfrowana asymetrycznie wiadomość.
    :return: Odszyfrowana wiadomość.
    """
    private_key = serialization.load_pem_private_key(key.encode(), password=None)
    decrypted = private_key.decrypt(
        base64.b64decode(encrypted_message),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None))
    return decrypted.decode()

def decrypt_message_symmetric(key,encrypted_message):
    """
    Odszyfrowuje przekazaną wiadomość z pomocą przekazanego klucza i zwraca tekst jawny.

    :param key: Klucz symetryczny.
    :param encrypted_message: Zaszyfrowana symetrycznie wiadomość.
    :return: Odszyfrowana wiadomość.
    """
    f = Fernet(key.encode())
    decrypted = f.decrypt(encrypted_message.encode())
    return decrypted.decode()