"""
Moduł zawierający logikę klienta. Odpowiada za wysyłanie żądań do serwera w celu rejestracji, logowania,
zarządzania zaproszeniami oraz prowadzenia rozmów. Funkcje obsługują dołączanie wymaganych danych do żądań,
zarządzanie tokenami JWT zapisanymi lokalnie (np. w Windows Credentials) oraz wymianę kluczy szyfrujących.
"""

import requests
import keyring
import pyqrcode
import pyotp
import encryption_management

SERVER_URL = "https://127.0.0.1:5000"

def register(username,password):
    """
    Wysyła żądanie do serwera zawierające nazwę i hasło użytkownika w celu rejestracji konta oraz otrzymania tokenu JWT
    potwierdzającego tożsamość użytkownika. Jeśli token znajduje się w otrzymanej odpowiedzi, zostaje on zapisany lokalnie
    z użyciem keyring (np. w Windows Credential Manager). W przypadku prawidłowej rejestracji serwer zwraca również sekretny
    klucz, na podstawie którego wygenerowany zostaje kod QR pozwalający na powiązanie konta z aplikacją autoryzacyjną w celu
    korzystania z uwierzytelniania dwuskładnikowego.

    :param username: Nazwa użytkownika.
    :param password: Hasło użytkownika.
    :return: Status odpowiedzi serwera (200 - sukces, 400 - błąd).
    """
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
    """
    Wysyła żądanie do serwera zawierające nazwę i hasło użytkownika w celu otrzymania tymczasowego tokena JWT dającego dostęp
    do weryfikacji TOTP. Jeśli token znajduje się w otrzymanej odpowiedzi, zostaje on zapisany lokalnie z użyciem keyring
    (np. w Windows Credential Manager).

    :param username: Nazwa użytkownika.
    :param password: Hasło użytkownika.
    :return: Status odpowiedzi serwera (200 - sukces, 400 - błąd).
    """
    response = requests.post(f"{SERVER_URL}/login",json={"username":username,"password":password},verify=False)
    if 'token' in list(response.json().keys()):
        try:
            keyring.delete_password("Chattersi",username)
        except keyring.errors.PasswordDeleteError:
            pass
        keyring.set_password('Chattersi',username,(response.json())['token'])
    return response.json()['status']

def logout(username):
    """
    Z pomocą keyring usuwa lokalnie zapisany token JWT dla danego użytkownika.

    :param username: Nazwa użytkownika.
    """
    try:
        keyring.delete_password("Chattersi",username)
    except keyring.errors.PasswordDeleteError:
        pass

def verify_totp(username,totp_code):
    """
    Wysyła żądanie do serwera zawierające kod TOTP oraz tymczasowy token JWT w celu otrzymania tokenu JWT potwierdzającego
    tożsamość użytkownika. Jeśli token znajduje się w otrzymanej odpowiedzi, zostaje on zapisany lokalnie z użyciem keyring
    (np. w Windows Credential Manager).

    :param username: Nazwa użytkownika.
    :param totp_code: 6-cyfrowy kod TOTP do weryfikacji.
    :return: Status odpowiedzi serwera (200 - sukces, 400 - błąd).
    """
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
    """
    Wysyła żądanie do serwera zawierające nazwę zapraszanego użytkownika, token JWT potwierdzający tożsamość użytkownika
    oraz klucz publiczny (jeden z dwóch kluczy asymetrycznych wygenerowanych w ramach funkcji). Klucz prywatny zostaje
    zapisany lokalnie na urządzeniu użytkownika. Celem żądania jest zaproszenie użytkownika do rozmowy.

    :param username: Nazwa użytkownika.
    :param user: Nazwa zapraszanego użytkownika.
    :return: Status odpowiedzi serwera (200 - sukces, 400 - błąd).
    """
    token = keyring.get_password('Chattersi',username)
    private_key,public_key = encryption_management.generate_asymmetric_keys()
    encryption_management.save_key(private_key,user,True)
    response = requests.post(f"{SERVER_URL}/invite", json={"user":user,"key":public_key,"token":token},verify=False)
    return response.json()['status']

def reply_to_invitation(username,user,decision):
    """
    Wysyła żądanie do serwera zawierające nazwę użytkownika, który wysłał zaproszenie, token JWT potwierdzający tożsamość
    użytkownika oraz odpowiedź na zaproszenie. Jeśli decyzją jest 'accept' i wszystko przebiegło prawidłowo to zaproszenie
    zostało zaakceptowane, a odpowiedź serwera zawiera klucz publiczny wysłany przez zapraszającego. Z jego pomocą zostaje
    zaszyfrowany klucz symetryczny wygenerowany podczas działania tej funkcji. Klucz symetryczny zostaje zapisany lokalnie
    na urządzeniu użytkownika oraz w swojej zaszyfrowanej wersji wysłany do serwera w celu przechowania go dopóki nie pobierze
    go osoba zapraszająca. Jeśli decyzją jest 'decline' zaproszenie zostaje odrzucone (klucz symetryczny nie jest generowany).

    :param username: Nazwa użytkownika.
    :param user: Nazwa użytkownika, który wysłał zaproszenie.
    :param decision: Odpowiedź na zaproszenie ('accept' - akceptacja zaproszenia, 'decline' - odrzucenie zaproszenia).
    :return: Status odpowiedzi serwera (200 - sukces, 400 - błąd).
    """
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
    """
    Wysyła żądanie do serwera zawierające typ pokoju ('chats' - rozmowy, 'invitations' - zaproszenia) oraz token JWT potwierdzający
    tożsamość użytkownika. Celem żądania jest uzyskanie listy nazw użytkowników zaproszonych lub będących częścią już zaakceptowanych
    rozmów.

    :param username: Nazwa użytkownika.
    :param room_type: Typ pokoju ('chats' - rozmowy, 'invitations' - zaproszenia).
    :return: Status odpowiedzi serwera (200 - sukces, 400 - błąd) oraz lista nazw użytkowników zaproszonych lub będących częścią rozmów.
    """
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/getrooms", json={"room_type":room_type,"token":token},verify=False)
    return response.json()['status'],response.json()['users']

def get_room_code(username,user):
    """
    Wysyła żądanie do serwera zawierające nazwę użytkownika oraz token JWT potwierdzający tożsamość użytkownika. Celem żądania jest
    otrzymanie identyfikatora rozmowy, do której należą obaj użytkownicy. Jeśli żądanie wysłał autor rozmowy i jest to jego pierwsze
    takie żądanie to odpowiedź serwera będzie zawierała również zaszyfrowany asymetrycznie klucz symetryczny, który zostanie odszyfrowany
    i zapisany lokalnie na urządzeniu użytkownika.

    :param username: Nazwa użytkownika.
    :param user: Nazwa użytkownika, który jest drugim uczestnikiem rozmowy. 
    :return: Status odpowiedzi serwera (200 - sukces, 400 - błąd) oraz identyfikator rozmowy.
    """
    token = keyring.get_password('Chattersi',username)
    response = requests.post(f"{SERVER_URL}/getcode", json={"user":user,"token":token},verify=False)
    if 'key' in list(response.json().keys()):
        symmetric_key = encryption_management.decrypt_message_asymmetric(encryption_management.get_key(user,True),(response.json())['key'])
        encryption_management.delete_tmp_key(user)
        encryption_management.save_key(symmetric_key,user,False)
    return response.json()['status'],response.json()['room_code']

def send_message(username,room_code,user,message,date):
    """
    Wysyła żądanie do serwera zawierające wiadomość (zaszyfrowaną kluczem symetrycznym) wraz z datą, identyfikator rozmowy oraz token JWT
    potwierdzający tożsamość użytkownika. Celem żądania jest wysłanie do serwera wiadmości w ramach rozmowy wskazanej identyfikatorem. Zostanie
    tam przechowana dopóki nie odbierze jej drugi użytkownik.

    :param username: Nazwa użytkownika.
    :param room_code: Identyfikator rozmowy.
    :param user: Nazwa użytkownika, który jest odbiorcą wiadomości.
    :param message: Treść wiadomości.
    :param date: Data wysłania wiadomości.
    :return: Status odpowiedzi serwera (200 - sukces, 400 - błąd).
    """
    token = keyring.get_password('Chattersi',username)
    symmetric_key = encryption_management.get_key(user,False)
    final_message = [encryption_management.encrypt_message_symmetric(symmetric_key,message),date]
    response = requests.post(f"{SERVER_URL}/send", json={"room_code":room_code,"message":final_message,"token":token},verify=False)
    return response.json()['status']

def get_messages(username,room_code,user):
    """
    Wysyła żądanie do serwera zawierające identyfikator rozmowy, nazwę użytkownika, który jest autorem odbieranych wiadomości oraz token JWT
    potwierdzający tożsamość użytkownika. Celem żądania jest uzyskanie listy list, gdzie każda pomniejsza lista zawiera wiadomość zaszyfrowaną
    kluczem symetrycznym oraz datę wysłania tej wiadomości.

    :param username: Nazwa użytkownika.
    :param room_code: Identyfikator rozmowy.
    :param user: Nazwa użytkownika, który jest nadawcą wiadomości.
    :return: Status odpowiedzi serwera (200 - sukces, 400 - błąd) oraz lista list, gdzie każda pomniejsza lista zawiera wiadomość zaszyfrowaną kluczem symetrycznym oraz datę wysłania tej wiadomości.
    """
    token = keyring.get_password('Chattersi',username)
    symmetric_key = encryption_management.get_key(user,False)
    response = requests.post(f"{SERVER_URL}/get", json={"room_code":room_code,"token":token},verify=False)
    messages = [[encryption_management.decrypt_message_symmetric(symmetric_key,message),timestamp] for message,timestamp in (response.json())['messages']]
    return response.json()['status'],messages