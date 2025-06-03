"""
Moduł odpowiadający za lokalne zarządzanie historią wiadomości między użytkownikami po stronie aplikacji klienta. Klasa
mieszcząca się w ramach moudłu posiada metody pozwalające na zapis wiadomości wysłanych lokalnie i otrzymanych z serwera
oraz odczyt wszystkich wiadomości lub dowolnej liczby ostatnich wiadomości. Wszystkie dane są zapisywane w formacie JSON
w folderze messages.
"""

import json
import os

class ChatDatabase:
    """
    Klasa do zarządzania lokalną historią rozmów pomiędzy dwoma użytkownikami.
    """
    def __init__(self, user1, user2):
        """
        Inicjalizuje obiekt ChatDatabase, tworzy folder messages i pusty plik JSON jeśli jeszcze nie istnieją. Nazwa pliku
        powstaje poprzez połączenie w kolejności alfabetycznej nazw obu uczestników rozmowy znakiem _.

        :param user1: Nazwa uczestnika rozmowy.
        :param user2: Nazwa drugiego uczestnika rozmowy.
        """
        self.directory = "messages"
        self.filename = f"{min(user1, user2)}_{max(user1, user2)}.json"
        self.filepath = os.path.join(self.directory, self.filename)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(self.filepath):
            self._initialize_file()
    def _initialize_file(self):
        """
        Tworzy pusty plik JSON reprezentujący rozmowę, jeśli jeszcze nie istnieje.
        """
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=3)
    def load_messages(self):
        """
        Odczytuje całą zawartość pliku JSON stanowiącego historię wiadomości danej rozmowy.

        :return: Słownik zawierający wszystkie wiadomości będące częścią danej rozmowy.
        """
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    def save_message(self, tresc, data, autor):
        """
        Zapisuje pojedynczą wiadomość do pliku rozmowy (treść, autor, data). Kluczami odpowiadającymi wiadomościom są
        liczby od 0 w zwyż.

        :param tresc: Treść wiadomości.
        :param data: Data wysłania wiadomości (z założenia ma format %d-%m-%Y %H:%M:%S).
        :param autor: Autor wiadomości.
        """
        messages = self.load_messages()
        last_index = max(map(int, messages.keys()), default=-1) + 1
        messages[str(last_index)] = {
            "tresc": tresc,
            "autor": autor,
            "data": data
        }
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=3)
    def save_messages_from_server(self, message_list, autor="Inny"):
        """
        Zapisuje wiadomości odebrane z serwera. Odebrana z serwera lista zawiera pomniejsze listy, gdzie każda pomniejsza
        lista składa się z treści wiadomości i daty ( [[treść,data],[treść,data]] ). Po dołączeniu wiadomości z serwera do
        uprzednio wczytanych wiadomości, wszystkie wiadomości są sortowane po dacie przed zapisaniem do pliku rozmowy.


        :param message_list: Lista list, gdzie każda pomniejsza lista składa się z treści i daty ( [[treść,data],[treść,data]] ).
        :param autor: Autor wiadomości odebranych z serwera.
        """
        messages = self.load_messages()
        last_index = max(map(int, messages.keys()), default=-1) + 1  
        for content, date in message_list:
            messages[str(last_index)] = {
                "tresc": content,
                "autor": autor,
                "data": date
            }
            last_index += 1
        sorted_msgs = sorted(messages.items(), key=lambda item: item[1]["data"])
        messages = {str(i): msg for i, (_, msg) in enumerate(sorted_msgs)}
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=3)
    def get_last_messages(self, count=5):
        """
        Zwraca wskazaną przez parametr count liczbę ostatnich wiadomości wysłanych w ramach rozmowy.

        :param count: Liczba ostatnich wiadomości do zwrócenia.
        :return: Lista słowników reprezentujących wiadomości.
        """
        messages = self.load_messages()
        if not messages:
            return []
        last_keys = sorted(map(int, messages.keys()))[-count:]
        return [messages[str(k)] for k in last_keys]