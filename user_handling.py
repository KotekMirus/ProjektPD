"""
Moduł odpowiedzialny za logikę użytkownika po stronie serwera. Obsługuje procesy rejestracji, weryfikacji prawidłowości danych
logowania (w tym TOTP), zarządzania pokojami. Odpowiada za zapisywanie danych użytkowników w pliku users.json.
"""

import json
import os
import bcrypt
import pyotp

class user:
    """
    Klasa reprezentująca użytkownika. Zawiera metody obsługujące rejestrację, logowanie, uwierzytelnianie dwuskładnikowe (TOTP)
    oraz zarządzanie przypisanymi i oczekującymi pokojami użytkownika.
    """
    def __init__(self,username,password):
        """
        Inicjalizuje obiekt użytkownika z podaną nazwą i hasłem.

        :param username: Nazwa użytkownika.
        :param password: Hasło użytkownika.
        """
        self.username = username
        self.password = password
    def register(self):
        """
        Rejestruje nowego użytkownika o ile nie istnieje użytkownik z podaną nazwą. Zapisuje podane nazwę i hasło oraz sekretny
        klucz wygenerowany na potrzeby uwierzytelniania dwuskładnikowego (2FA).

        :return: True jeśli rejestracja przebiegła pomyślnie, False jeśli użytkownik już istnieje.
        """
        self.check_structure_existence()
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        if self.username in list(users.keys()):
            return False
        else:
            self.secret_key = pyotp.random_base32()
            self.save()
            return True
    def check_structure_existence(self):
        """
        Sprawdza czy istnieje folder data. Jeśli nie istnieje to go tworzy. Sprawdza czy w folderze data znajduje się plik
        users.json. Jeśli nie to go tworzy.
        """
        if os.path.isdir('data') == False:
            os.mkdir('data')
        if os.path.isfile('data/users.json') == False:
            with open('data/users.json','w') as file:
                json.dump({}, file, indent = 3)
    def save(self):
        """
        Zapisuje dane użytkownika (nazwę, sekretny klucz będący częścią mechanizmu TOTP oraz hasz hasła z solą) w pliku users.json.
        """
        self.check_structure_existence()
        hash_password = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode()
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        users[self.username] = {"hash_password":hash_password,"secret_key":self.secret_key,"rooms":[],"pending_rooms":[]}
        with open('data/users.json','w') as file:
            json.dump(users, file, indent = 3)
    def verify(self):
        """
        Sprawdza czy nazwa i hasło przekazane przy iniclizacji obiektu są zgodne z tymi przechowywanymi w pliku users.json.
        
        :return: True jeśli dane logowania są poprawne, False w przeciwnym przypadku.
        """
        self.check_structure_existence()
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        if self.username in list(users.keys()):
            found_user = users[self.username]
            check_password_result = bcrypt.checkpw(self.password.encode(),found_user['hash_password'].encode())
            return check_password_result
        else:
            return False
    def verify_totp(self,totp_code):
        """
        Weryfikuje podany kod TOTP wykorzystując moduł pyotp i sekretny klucz zapisany w pliku users.json.

        :param totp_code: Kod TOTP.
        :return: True jeśli kod TOTP jest poprawny, False w przeciwnym przypadku.
        """
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        user_secret_key = pyotp.TOTP(users[self.username]["secret_key"])
        if user_secret_key.verify(totp_code,valid_window=1):
            return True
        else:
            return False
    def add_to_pending_room(self,room_code,remote_user,key):
        """
        Dodaje do sekcji oczekujących pokojów/rozmów obu uczestników rozmowy listę zawierającą identyfikator rozmowy
        oraz klucz publiczny będący częścią szyfrowania asymetrycznego.

        :param room_code: Identyfikator rozmowy.
        :param remote_user: Nazwa drugiego uczestnika rozmowy.
        :param key: Klucz publiczny.
        """
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        users[self.username]['pending_rooms'].append([room_code,key])
        users[remote_user]['pending_rooms'].append([room_code,key])
        with open('data/users.json','w') as file:
            json.dump(users, file, indent = 3)
    def get_room_codes(self):
        """
        Zwraca dwie listy, listę identyfikatorów zaakceptowanych rozmów oraz listę identyfikatorów zaproszeń dla
        użytkownika o nazwie przekazanej podczas inicjalizacji obiektu.
        
        :return: Lista identyfikatorów zaakceptowanych rozmów oraz lista identyfikatorów zaproszeń.
        """
        self.check_structure_existence()
        users = None
        with open('data/users.json','r') as file:
            users = json.load(file)
        accepted = users[self.username]['rooms']
        pending = [element[0] for element in users[self.username]['pending_rooms']]
        return accepted,pending