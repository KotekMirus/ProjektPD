import json
import os
from datetime import datetime

class ChatDatabase:
    def __init__(self, user1, user2, directory="message"):
        #Tworzy plik rozmowy między user1 i user2.
        
        # Pobranie ścieżki do katalogu, w którym jest uruchomiony skrypt
        base_dir = os.path.dirname(os.path.abspath(__file__))  
        self.directory = os.path.join(base_dir, "message")  # Folder "message" w katalogu aplikacji
        self.filename = f"{min(user1, user2)}_{max(user1, user2)}.json"
        self.filepath = os.path.join(self.directory, self.filename)

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)  # Tworzy folder 'message', jeśli nie istnieje

        if not os.path.exists(self.filepath):
            self._initialize_file()

    def _initialize_file(self):
        #Tworzy pusty plik JSON dla danej rozmowy
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=3)

    def load_messages(self):
        #Ładuje wszystkie wiadomości rozmowy
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_message(self, tresc, autor):
        #Zapisuje nową wiadomość do pliku rozmowy
        messages = self.load_messages()
        
        # Znalezienie kolejnego numeru wiadomości
        last_index = max(map(int, messages.keys()), default=-1) + 1

        messages[str(last_index)] = {
            "tresc": tresc,
            "autor": autor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Aktualna data
        }

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=3)

    def get_last_messages(self, count=5):
        #Pobiera ostatnie wiadomości rozmowy
        messages = self.load_messages()
        if not messages:
            return []

        last_keys = sorted(map(int, messages.keys()))[-count:]
        return [messages[str(k)] for k in last_keys]

# ------------------------
"""if __name__ == "__main__":
    # Tworzy rozmowe między Janem a Anną
    chat = ChatDatabase("Jan", "Anna")

    # Zapisywanie wiadomości
    chat.save_message("Hej, co tam?", "Jan")
    chat.save_message("Wszystko ok, a u Ciebie?", "Anna")

    # Pobieranie wiadomości
    print("Ostatnie 2 wiadomości:")
    print(chat.get_last_messages(count=3))"""
