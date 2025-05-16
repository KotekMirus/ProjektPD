import json
import os

class ChatDatabase:
    def __init__(self, user1, user2):
        #Tworzy plik rozmowy między user1 i user2.
        self.directory = "messages"  # Folder "messages" w katalogu aplikacji
        self.filename = f"{min(user1, user2)}_{max(user1, user2)}.json"
        self.filepath = os.path.join(self.directory, self.filename)

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)  # Tworzy folder 'messages', jeśli nie istnieje

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

    def save_message(self, tresc, data, autor):
        #Zapisuje nową wiadomość do pliku rozmowy
        messages = self.load_messages()
        
        # Znalezienie kolejnego numeru wiadomości
        last_index = max(map(int, messages.keys()), default=-1) + 1

        messages[str(last_index)] = {
            "tresc": tresc,
            "autor": autor,
            "data": data  # Aktualna data
        }

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=3)

    def save_messages_from_server(self, message_list, autor="Inny"):
        """
        Zapisuje wiadomości odebrane z serwera.
        Każda wiadomość to lista: [tresc, data]
        """
        messages = self.load_messages()
        
        # Znajdujemy najwyższy aktualny indeks
        last_index = max(map(int, messages.keys()), default=-1) + 1
        
        for content, date in message_list:
            messages[str(last_index)] = {
                "tresc": content,
                "autor": autor,
                "data": date  # data pochodzi z serwera!
            }
            last_index += 1

        # Sortujemy wszystkie wiadomości po dacie
        sorted_msgs = sorted(messages.items(), key=lambda item: item[1]["data"])
        messages = {str(i): msg for i, (_, msg) in enumerate(sorted_msgs)}

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=3)

            

    def get_last_messages(self, count=5):
        #Pobiera ostatnie wiadomości rozmowy
        messages = self.load_messages()
        if not messages:
            return []

        last_keys = sorted(map(int, messages.keys()))[-count:]
        return [messages[str(k)] for k in last_keys]


    def simulate_server_response():
        return {
            "message": "Poprawnie odświeżono stan otrzymanych wiadomości",
            "status": 200,
            "messages": [
                ["Hejo, mam jedną sprawę", "2025-04-04 13:10:11"],
                ["Jest promocja na Funko Pop", "2025-04-04 13:10:48"],
                ["Kup mi Gandalfa", "2025-04-04 13:11:23"]
            ]
        }