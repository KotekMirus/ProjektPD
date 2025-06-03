"""
Moduł zawierający klasę, której metody odpowiadają za tworzenie i modyfikowanie graficznego interfejsu użytkownika.
"""

import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Entry, Button, Checkbutton
from ttkbootstrap.widgets import Label as WarningLabel
from logic import ChatDatabase
import time
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import client
import os

class Chattersi:
    """
    Klasa, której metody odpowiadają za tworzenie i modyfikowanie graficznego interfejsu użytkownika.
    """
    def __init__(self):
        """
        Inicjalizuje główne okno aplikacji, ustawia styl, ikonę i rozmiar okna oraz wywołuje wyświetlenie ekranu logowania.
        """
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("Chattersi")
        self.root.geometry("400x550")
        self.style = Style("solar")
        self.selected_chat = tk.StringVar()
        self.root.iconbitmap('images/ikona.ico')
        self.username = None
        self.current_roommate = None
        self.current_room_code = None
        self.show_login()
    def show_login(self):
        """
        Wyświetla formularz logowania, który pozwala na wprowadzenie nazwy oraz hasła użytkownika i przejście do logowania
        lub formularza rejestracji.
        """
        self.clear_frame()
        tk.Label(self.root, text="Logowanie", font=("Arial", 18)).pack(pady=15)
        tk.Label(self.root, text="Nazwa", font=("Arial", 8)).pack(pady=1)
        entry_nazwa = tk.Entry(self.root, width=30, fg="gray")
        entry_nazwa.insert(0, "Nazwa")
        entry_nazwa.bind("<FocusIn>", lambda e: entry_nazwa.delete(0, tk.END) if entry_nazwa.get() == "Nazwa" else None)
        entry_nazwa.bind("<FocusOut>", lambda e: entry_nazwa.insert(0, "Nazwa") if entry_nazwa.get() == "" else None)
        entry_nazwa.pack(pady=5, ipady=5)
        tk.Label(self.root, text="Hasło", font=("Arial", 8)).pack(pady=1)
        entry_haslo = tk.Entry(self.root, width=30, fg="gray", show="*")
        entry_haslo.insert(0, "Hasło")
        entry_haslo.bind("<FocusIn>", lambda e: entry_haslo.delete(0, tk.END) if entry_haslo.get() == "Hasło" else None)
        entry_haslo.bind("<FocusOut>", lambda e: entry_haslo.insert(0, "Hasło") if entry_haslo.get() == "" else None)
        entry_haslo.pack(pady=5, ipady=5)
        Button(self.root, text="Zaloguj", bootstyle="info", command=lambda: self.login(entry_nazwa.get(),entry_haslo.get())).pack(pady=5)
        Button(self.root, text="Zarejestruj", bootstyle="success", command=self.show_register).pack(pady=5)
    def login(self,username,password):
        """
        Obsługuje logowanie użytkownika. Korzysta z funkcji login() modułu client. Jeśli logowanie powiodło się, wywołuje
        wyświetlenie formularza weryfikacji TOTP. W przeciwnym przypadku wraca do formularza logowania.

        :param username: Nazwa użytkownika.
        :param password: Hasło użytkownika.
        """
        status = client.login(username,password)
        if status == 200:
            self.username = username
            self.show_totp()
        else:
            self.show_login()
            WarningLabel(self.root, text="Nieprawidłowe dane logowania", bootstyle="danger", wraplength=380, font=("Arial", 12)).pack(pady=1)
    def show_register(self):
        """
        Wyświetla formularz rejestracji konta, który pozwala na wprowadzenie nazwy oraz hasła użytkownika (dwa razy) i przejście
        do rejestracji lub powrót do formularza logowania.
        """
        self.clear_frame()
        tk.Label(self.root, text="Rejestracja", font=("Arial", 18)).pack(pady=15)
        tk.Label(self.root, text="Nazwa", font=("Arial", 8)).pack(pady=1)
        entry_nazwa = tk.Entry(self.root, width=30, fg="gray")
        entry_nazwa.insert(0, "Nazwa")
        entry_nazwa.bind("<FocusIn>", lambda e: entry_nazwa.delete(0, tk.END) if entry_nazwa.get() == "Nazwa" else None)
        entry_nazwa.bind("<FocusOut>", lambda e: entry_nazwa.insert(0, "Nazwa") if entry_nazwa.get() == "" else None)
        entry_nazwa.pack(pady=5, ipady=5)
        tk.Label(self.root, text="Hasło", font=("Arial", 8)).pack(pady=1)
        entry_haslo = tk.Entry(self.root, width=30, fg="gray", show="*")
        entry_haslo.insert(0, "Hasło")
        entry_haslo.bind("<FocusIn>", lambda e: entry_haslo.delete(0, tk.END) if entry_haslo.get() == "Hasło" else None)
        entry_haslo.bind("<FocusOut>", lambda e: entry_haslo.insert(0, "Hasło") if entry_haslo.get() == "" else None)
        entry_haslo.pack(pady=5, ipady=5)
        tk.Label(self.root, text="Powtórz hasło", font=("Arial", 8)).pack(pady=1)
        entry_powtorz_h = tk.Entry(self.root, width=30, fg="gray", show="*")
        entry_powtorz_h.insert(0, "Powtórz hasło")
        entry_powtorz_h.bind("<FocusIn>", lambda e: entry_powtorz_h.delete(0, tk.END) if entry_powtorz_h.get() == "Powtórz hasło" else None)
        entry_powtorz_h.bind("<FocusOut>", lambda e: entry_powtorz_h.insert(0, "Powtórz hasło") if entry_powtorz_h.get() == "" else None)
        entry_powtorz_h.pack(pady=5, ipady=5)
        Button(self.root, text="Zarejestruj", bootstyle="success", command=lambda: self.register(entry_nazwa.get(),entry_haslo.get(),entry_powtorz_h.get())).pack(pady=5)
        Button(self.root, text="Wróć", bootstyle="warning", command=self.show_login).pack(pady=5)
    def register(self,username,password,repeated_password):
        """
        Obsługuje rejestrację konta użytkownika. Jeśli hasło i powtórzone hasło są takie same, korzysta z funkcji register()
        modułu client. Jeśli rejestracja powiodła się, wywołuje wyświetlenie kodu QR, który należy zeskanować aplikacją
        autentykacyjną w celu skonfigurowania uwierzytelniania dwuskładnikowego. W przeciwnym przypadku wyświetlone zostaje
        ostrzeżenie.

        :param username: Nazwa użytkownika.
        :param password: Hasło użytkownika.
        :param repeated_password: Powtórzone hasło użytkownika.
        """
        if password == repeated_password:
            status = client.register(username,password)
            if status == 200:
                self.username = username
                self.show_qr()
            else:
                self.show_register()
                WarningLabel(self.root, text="Nie można zarejestrować użytkownika o podanej nazwie lub o podanym haśle. Nazwa nie może być zajęta i musi zawierać od 3 do 32 znaków. Hasło musi zawierać od 12 do 64 znaków", bootstyle="danger", wraplength=380, font=("Arial", 12)).pack(pady=1)
        else:
            WarningLabel(self.root, text="Oba wprowadzone hasła muszą być takie same", bootstyle="danger", wraplength=380, font=("Arial", 12)).pack(pady=1)
    def show_totp(self):
        """
        Wyświetla formularz weryfikacji TOTP, który zawiera pole do wprowadzenia jednorazowego kodu TOTP i przycisk pozwalający
        przejść do weryfikacji.
        """
        self.clear_frame()
        tk.Label(self.root, text="Podaj TOTP", font=("Arial", 16)).pack(pady=10)
        entry = tk.Entry(self.root, width=30, fg="gray")
        entry.insert(0, "Kod TOTP")
        entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END) if entry.get() == "Kod TOTP" else None)
        entry.bind("<FocusOut>", lambda e: entry.insert(0, "Kod TOTP") if entry.get() == "" else None)
        entry.pack(pady=5, ipady=5)
        Button(self.root, text="Zweryfikuj", bootstyle="info", command=lambda: self.verify_totp(entry.get())).pack(pady=5)
    def verify_totp(self,totp_code):
        """
        Obsługuje weryfikację TOTP. Korzysta z funkcji verify_totp() modułu client. Jeśli weryfikacja przebiegła poprawnie,
        zostaje wywołane wyświetlenie listy rozmów. W przeciwnym przypadku zostaje wyświetlone ostrzeżenie.

        :param totp_code: Jednorazowy, 6-cyfrowy kod TOTP.
        """
        status = client.verify_totp(self.username,totp_code)
        if status == 200:
            self.show_chats()
        else:
            self.show_totp()
            WarningLabel(self.root, text="Nieprawidłowy kod TOTP", bootstyle="danger", wraplength=380, font=("Arial", 12)).pack(pady=1)
    def show_qr(self):
        """
        Wyświetla kod QR, który należy zeskanować aplikacją autentykacyjną w celu skonfigurowania uwierzytelniania dwuskładnikowego.
        """
        self.clear_frame()
        tk.Label(self.root, text="Zeskanuj kod QR", font=("Arial", 16)).pack(pady=10)
        image = Image.open(f"images/{self.username}_qr_code.png")
        self.qr_img = ImageTk.PhotoImage(image)
        tk.Label(self.root, image=self.qr_img).pack(pady=10)
        tk.Label(self.root, text="Zeskanuj kod QR za pomocą aplikacji uwierzytelniającej na swoim telefonie, następnie naciśnij przycisk Dalej", font=("Arial", 11), wraplength=250).pack(pady=10)
        Button(self.root, text="Dalej", bootstyle="info", command=self.confirm_totp_scanning).pack(pady=5)
    def confirm_totp_scanning(self):
        """
        Usuwa plik zawierający kod QR, który pozwala na przekazanie do aplikacji autentykacyjnej sekretnego klucza wykorzystywanego
        podczas konfiguracji TOTP, kiedy nie jest już potrzebny. Następnie wywołuje wyświetlenie listy rozmów.
        """
        if os.path.isfile(f"images/{self.username}_qr_code.png"):
            os.remove(f"images/{self.username}_qr_code.png")
        self.show_chats()
    def show_chats(self):
        """
        Wyświetla listę rozmów, która ma formę możliwych do scrollowania ramek, gdzie do każdej ramki przyporządkowany jest
        przycisk typu RadioButton. Można wybrać maksymalnie jedną rozmowę na raz, wybranie innej odznacza RadioButton poprzedniej.
        Lista nazw użytkowników wyświetlanych w ramkach rozmów jest pobierana z serwera przez wywołaną w tej metodzie funkcję
        get_chat_members() z modułu client. Okno zawiera przyciski pozwalające na wywołanie: wyświetlenia wybranej rozmowy,
        wyświetlenia listy zaproszeń, wylogowania.
        """
        self.clear_frame()
        status, users = client.get_chat_members(self.username, 'chats')
        tk.Label(self.root, text="Wybierz rozmowę", font=("Arial", 16)).pack(pady=10)
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        conversations = ["Rozmowa z " + user for user in users]
        for conv in conversations:
            frame = tk.Frame(scrollable_frame, bg="#d9edf7", bd=2, relief=tk.RIDGE)
            frame.pack(fill=tk.X, padx=20, pady=5)
            radio = tk.Radiobutton(frame,text=conv,variable=self.selected_chat,value=conv,font=("Arial", 12),bg="#d9edf7",anchor='w')
            radio.pack(padx=10, pady=10, anchor='w')
        Button(self.root, text="Przejdź", bootstyle="info", command=self.show_check_chat).pack(pady=5)
        Button(self.root, text="Zaproszenia", bootstyle="success", command=self.show_invitations).pack(pady=5)
        Button(self.root, text="Wyloguj", bootstyle="danger", command=self.logout).pack(pady=5)
    def logout(self):
        """
        Obsługuje wylogowanie użytkownika poprzez wywołanie funkcji logout() z modułu client, która usuwa z urządzenia token
        JWT dla wskazanego użytkownika. Po wylogowaniu wywołuje wyświetlenie formularza logowania.
        """
        client.logout(self.username)
        self.username = None
        self.show_login()
    def show_invitations(self):
        """
        Wyświetla listę zaproszeń, która ma formę możliwych do scrollowania ramek, gdzie do każdej ramki przyporządkowane są
        dwa przyciski. Za pomocą pierwszego przycisku można zaakceptować zaproszenie, a za pomocą drugiego je odrzucić. Po
        wybraniu jednej z opcji, ramka znika z listy. Lista nazw użytkowników wyświetlanych w ramkach zaproszeń jest pobierana
        z serwera przez wywołaną w tej metodzie funkcję get_chat_members() z modułu client. Okno zawiera również pole do
        wprowadzenia nazwy użytkownika i przycisk pozwalający wysłać do niego zaproszenie poprzez wywołanie odpowiedniej metody
        tej klasy.
        """
        self.clear_frame()
        status,invitations = client.get_chat_members(self.username,'invitations')
        tk.Label(self.root, text="Zaproszenia", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text="Wyślij zaproszenie do:", font=("Arial", 12)).pack(pady=(15, 5))
        entry = Entry(self.root, width=30)
        entry.pack(pady=5)
        Button(self.root, text="Wyślij", bootstyle="info", command=lambda: self.invite(entry.get())).pack(pady=5)
        Button(self.root, text="Wróć", bootstyle="secondary", command=self.show_chats).pack(pady=15)
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        for user in invitations:
            frame = tk.Frame(scrollable_frame, bd=1, relief=tk.RIDGE, padx=10, pady=5)
            frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(frame, text=f"Zaproszenie od: {user}", font=("Arial", 12)).pack(side=tk.LEFT)
            btn_frame = tk.Frame(frame)
            btn_frame.pack(side=tk.RIGHT)
            Button(btn_frame, text="Akceptuj", bootstyle="success", command=lambda u=user: self.reply_to_invitation(u, 'accept')).pack(side=tk.LEFT, padx=5)
            Button(btn_frame, text="Odrzuć", bootstyle="danger", command=lambda u=user: self.reply_to_invitation(u, 'decline')).pack(side=tk.LEFT, padx=5)
    def invite(self,user):
        """
        Obsługuje wysłanie zaproszenia do podanego użytkownika. Korzysta z funkcji invite() modułu client. Jeśli zaproszenie
        użytkownika przebiegło prawidłowo, zostanie wyświetlony komunikat na ten temat. W przeciwnym przypadku zostanie
        wyświetlone ostrzeżenie.

        :param user: Nazwa zaproszonego użytkownika podana w oknie wyświetlającym listę zaproszeń.
        """
        status = client.invite(self.username,user)
        if status == 200:
            tk.messagebox.showinfo("Zaproszenie", "Zaproszenie zostało pomyślnie wysłane")
        else:
            tk.messagebox.showwarning("Zaproszenie", "Nie udało się wysłać zaproszenia. Podany użytkownik nie istnieje")
    def reply_to_invitation(self,user,decision):
        """
        Obsługuje odpowiedź na zaproszenie od podanego użytkownika. Korzysta z funkcji reply_to_invitation() modułu client.
        Jeśli użytkownik nacisnął w oknie wyświetlającym listę zaproszeń przycisk 'Akceptuj' to jako decyzja przekazane zostało
        'accept', czyli akceptacja zaproszenia. Analogicznie działa to dla przycisku 'Odrzuć' i decyzji 'decline'. Na koniec
        funkcji wywołane zostaje wyświetlenie listy zaproszeń.

        :param user: Nazwa użytkownika, który wysłał zaproszenie.
        :param decision: Odpowiedź na zaproszenie (powinno to być 'accept' lub 'decline').
        """
        client.reply_to_invitation(self.username,user,decision)
        self.show_invitations()
    def show_check_chat(self):
        """
        Sprawdza, czy użytkownik wybrał rozmowę (zaznaczył jeden z przycisków typu RadioButton). Jeśli tak to identyfikator rozmowy
        zostaje pobrany z serwera z pomocą funkcji get_room_code() modułu client. Jeśli pobranie identyfikatora się powiodło, dane
        aktualnej rozmowy zostają zapisane w odpowiednich polach klasy i zostaje wywołane wyświetlenie rozmowy. W przeciwnym przypadku
        zostaje wyświetlone ostrzeżenie.
        """
        if self.selected_chat.get():
            roommate = (self.selected_chat.get()).split()[-1]
            status,room_code = client.get_room_code(self.username,roommate)
            if status == 200:
                self.current_room_code = room_code
                self.current_roommate = roommate
                self.show_chat()
            else:
                tk.messagebox.showwarning("Brak dostępu", "Brak dostępu do wybranej rozmowy")
        else:
            tk.messagebox.showwarning("Brak wyboru", "Wybierz rozmowę by kontynuować")
    def show_chat(self):
        """
        Wyświetla rozmowę, czyli duże pole tekstowe przeznaczone do wyświetlania wiadomości oraz małe pole tekstowe do wprowadzenia
        nowej wiadomości wraz z przyciskiem 'Wyślij', który wywołuje metodę obsługującą wysłanie wiadomości. Zapisuje w polu klasy
        obiekt do obsługi bazy danych wiadomości i wyświetla wiadomości z pomocą metody load_chat_history().
        """
        self.clear_frame()
        Button(self.root, text="Cofnij", bootstyle="danger", command=self.end_chat).pack(pady=5)
        tk.Label(self.root, text=f"{self.selected_chat.get()}", font=("Arial", 16)).pack(pady=10)
        chat_name = self.selected_chat.get().replace("Rozmowa z ", "")
        self.chat_db = ChatDatabase(self.username, chat_name)
        self.chat_box = tk.Text(self.root, height=20, width=45, bg="#f8f9fa", fg="#212529")
        self.chat_box.pack(pady=5)
        self.load_chat_history()
        frame = tk.Frame(self.root)
        frame.pack(pady=5)
        self.chat_input = Entry(frame, width=30)
        self.chat_input.pack(side=tk.LEFT, padx=5)
        Button(frame, text="Wyślij", bootstyle="info", command=self.send_message).pack(side=tk.RIGHT, padx=5)
        self.load_chat_history()
        self.chat_box.see("end")
        self.root.after(1000,self.get_new_messages)
    def end_chat(self):
        """
        Kończy rozmowę poprzez zastąpienie wartości pól klasy związanych z aktualną rozmową wartościami None. Wywołuje wyświetlenie
        listy rozmów.
        """
        self.current_room_code = None
        self.current_roommate = None
        self.show_chats()
    def load_chat_history(self):
        """
        Korzystając z obiektu do obsługi bazy danych wiadomości przechowywanego w odpowiednim polu klasy, pobiera 100 ostatnich
        wiadomości. Odblokowuje możliwość edycji pola do wyświetlania wiadomości, czyści je i w pętli dodaje do niego pobrane
        wiadomości z uwzględnieniem pogrubienia odpowiednich elementów. Na koniec blokuje możliwość edycji pola do wyświetlania
        wiadomości.
        """
        messages = self.chat_db.get_last_messages(100)
        self.chat_box.config(state="normal")  
        self.chat_box.delete("1.0", tk.END)
        self.chat_box.tag_configure("bold", font=("Arial", 10, "bold"))
        for msg in messages:
            self.chat_box.insert(tk.END, f"{msg['data']}\n", "bold")
            self.chat_box.insert(tk.END, f"{msg['autor']}: ", "bold")
            self.chat_box.insert(tk.END, f"{msg['tresc']}\n\n")
        self.chat_box.config(state="disabled") 
    def get_new_messages(self):
        """
        Korzystając z funkcji get_messages() modułu client pobiera z serwera listę list, gdzie każda pomniejsza lista zawiera
        treść wiadomości i datę jej wysłania. Jeśli pobranie wiadomości powiodło się, zostają one zapisane lokalnie z pomocą
        save_messages_from_server(). Następnie sprawdzane jest czy użytkownik ma czat przewinięty do samego dołu (najświeższe
        wiadomości). Jeśli tak to pole wyświetlające wiadomości zostaje odświeżone (zaktualizowane o wyświetlanie nowych wiadmości)
        i widok zostaje z powrotem przewinięty na sam dół czatu. Jeśli użytkownik znajduje się w innym miejscu czatu to wiadomości
        zostają zapisane bez odświeżania pola wiadomości metodą load_chat_history(), aby nie przenieść go na siłę ze starego
        miejsca czatu, które przegląda, do samego dołu. Ostatnia linia kodu tej funkcji zapewnia automatyczne wywoływanie tej
        funkcji co sekundę.
        """
        status,messages = client.get_messages(self.username,self.current_room_code,self.current_roommate)
        if status == 200:
            self.chat_db.save_messages_from_server(messages,self.current_roommate)
            at_bottom = self.chat_box.yview()[1] == 1.0
            if at_bottom:
                self.load_chat_history()
                self.chat_box.see("end")
        self.root.after(1000,self.get_new_messages)
    def send_message(self):
        """
        Pobiera zawartość wpisaną przez użytkownika w pole wysyłania wiadomości. Jeśli zawartość nie jest pusta to odczytywana
        jest aktualna data i godzina i wiadomość zostaje wysłana do serwera z pomocą funkcji send_message() modułu client. Jeśli
        wysłanie powiodło się, wiadomość zostaje zapisana lokalnie, a pole wysyłania wiadomości wyczyszczone. Pole wyświetlania
        wiadomości zostaje odświeżone (zaktualizowane o nową wiadomość), a widok przewinięty na sam dół czatu.
        """
        tresc = self.chat_input.get().strip()
        if not tresc.strip():
            return
        message_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        status = client.send_message(self.username,self.current_room_code,self.current_roommate,tresc,message_date)
        if status == 200:
            self.chat_db.save_message(tresc,message_date,self.username)
            self.chat_input.delete(0, tk.END)
            self.load_chat_history()
            self.chat_box.see("end")
    def clear_frame(self):
        """
        Czyści wszystkie widżety z okna aplikacji.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
    def run(self):
        """
        Uruchamia główną pętlę tkintera.
        """
        self.root.mainloop()