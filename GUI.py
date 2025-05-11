import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Entry, Button, Checkbutton
from logic import ChatDatabase
import time
from tkinter import messagebox
from PIL import Image, ImageTk
import client
import os

class Chattersi:
    def __init__(self):
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
        self.clear_frame()
        tk.Label(self.root, text="Logowanie", font=("Arial", 18)).pack(pady=15)
        #Nazwa
        tk.Label(self.root, text="Nazwa", font=("Arial", 8)).pack(pady=1)
        entry_nazwa = tk.Entry(self.root, width=30, fg="gray")
        entry_nazwa.insert(0, "Nazwa")
        entry_nazwa.bind("<FocusIn>", lambda e: entry_nazwa.delete(0, tk.END) if entry_nazwa.get() == "Nazwa" else None)
        entry_nazwa.bind("<FocusOut>", lambda e: entry_nazwa.insert(0, "Nazwa") if entry_nazwa.get() == "" else None)
        entry_nazwa.pack(pady=5, ipady=5)
        #haslo
        tk.Label(self.root, text="Hasło", font=("Arial", 8)).pack(pady=1)
        entry_haslo = tk.Entry(self.root, width=30, fg="gray", show="*")
        entry_haslo.insert(0, "Hasło")
        entry_haslo.bind("<FocusIn>", lambda e: entry_haslo.delete(0, tk.END) if entry_haslo.get() == "Hasło" else None)
        entry_haslo.bind("<FocusOut>", lambda e: entry_haslo.insert(0, "Hasło") if entry_haslo.get() == "" else None)
        entry_haslo.pack(pady=5, ipady=5)
        Button(self.root, text="Zaloguj", bootstyle="info", command=lambda: self.login(entry_nazwa.get(),entry_haslo.get())).pack(pady=5)
        Button(self.root, text="Zarejestruj", bootstyle="success", command=self.show_register).pack(pady=5)
    
    def login(self,username,password):
        status = client.login(username,password)
        if status == 200:
            self.username = username
            self.show_totp()
        else:
            self.show_login()
    
    def show_register(self):
        self.clear_frame()
        tk.Label(self.root, text="Rejestracja", font=("Arial", 18)).pack(pady=15)
        #Nazwa
        tk.Label(self.root, text="Nazwa", font=("Arial", 8)).pack(pady=1)
        entry_nazwa = tk.Entry(self.root, width=30, fg="gray")
        entry_nazwa.insert(0, "Nazwa")
        entry_nazwa.bind("<FocusIn>", lambda e: entry_nazwa.delete(0, tk.END) if entry_nazwa.get() == "Nazwa" else None)
        entry_nazwa.bind("<FocusOut>", lambda e: entry_nazwa.insert(0, "Nazwa") if entry_nazwa.get() == "" else None)
        entry_nazwa.pack(pady=5, ipady=5)
        #Haslo
        tk.Label(self.root, text="Hasło", font=("Arial", 8)).pack(pady=1)
        entry_haslo = tk.Entry(self.root, width=30, fg="gray", show="*")
        entry_haslo.insert(0, "Hasło")
        entry_haslo.bind("<FocusIn>", lambda e: entry_haslo.delete(0, tk.END) if entry_haslo.get() == "Hasło" else None)
        entry_haslo.bind("<FocusOut>", lambda e: entry_haslo.insert(0, "Hasło") if entry_haslo.get() == "" else None)
        entry_haslo.pack(pady=5, ipady=5)
        #Powtórz Hasło
        tk.Label(self.root, text="Powtórz hasło", font=("Arial", 8)).pack(pady=1)
        entry_powtorz_h = tk.Entry(self.root, width=30, fg="gray", show="*")
        entry_powtorz_h.insert(0, "Powtórz hasło")
        entry_powtorz_h.bind("<FocusIn>", lambda e: entry_powtorz_h.delete(0, tk.END) if entry_powtorz_h.get() == "Powtórz hasło" else None)
        entry_powtorz_h.bind("<FocusOut>", lambda e: entry_powtorz_h.insert(0, "Powtórz hasło") if entry_powtorz_h.get() == "" else None)
        entry_powtorz_h.pack(pady=5, ipady=5)
        Button(self.root, text="Zarejestruj", bootstyle="success", command=lambda: self.register(entry_nazwa.get(),entry_haslo.get(),entry_powtorz_h.get())).pack(pady=5)
        Button(self.root, text="Wróć", bootstyle="warning", command=self.show_login).pack(pady=5)
    
    def register(self,username,password,repeated_password):
        if password == repeated_password:
            status = client.register(username,password)
            if status == 200:
                self.username = username
                self.show_qr()
            else:
                self.show_register()

    def show_totp(self):
        self.clear_frame()
        tk.Label(self.root, text="Podaj TOTP", font=("Arial", 16)).pack(pady=10)
        entry = tk.Entry(self.root, width=30, fg="gray")
        entry.insert(0, "Kod TOTP")
        entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END) if entry.get() == "Kod TOTP" else None)
        entry.bind("<FocusOut>", lambda e: entry.insert(0, "Kod TOTP") if entry.get() == "" else None)
        entry.pack(pady=5, ipady=5)
        Button(self.root, text="Zweryfikuj", bootstyle="info", command=lambda: self.verify_totp(entry.get())).pack(pady=5)
        #Button(self.root, text="Cofnij", bootstyle="danger", command=self.show_login).pack(pady=5)

    def verify_totp(self,totp_code):
        status = client.verify_totp(self.username,totp_code)
        if status == 200:
            self.show_chats()
        else:
            self.show_totp()

    def show_qr(self):
        self.clear_frame()
        tk.Label(self.root, text="Zeskanuj kod QR", font=("Arial", 16)).pack(pady=10)
        #tk.Label(self.root, text="TU WYSWIETLI SIE KOD", font=("Arial", 16)).pack(pady=10)
        image = Image.open(f"images/{self.username}_qr_code.png")
        self.qr_img = ImageTk.PhotoImage(image)  # Musi być przypisane do self, by nie zostało usunięte z pamięci
        tk.Label(self.root, image=self.qr_img).pack(pady=10)
        tk.Label(self.root, text="Zeskanuj kod QR za pomocą aplikacji uwierzytelniającej na swoim telefonie, następnie naciśnij przycisk Dalej", font=("Arial", 11), wraplength=250).pack(pady=10)
        Button(self.root, text="Dalej", bootstyle="info", command=self.confirm_totp_scanning).pack(pady=5)
        #Button(self.root, text="Cofnij", bootstyle="danger", command=self.show_login).pack(pady=5)

    def confirm_totp_scanning(self):
        if os.path.isfile(f"images/{self.username}_qr_code.png"):
            os.remove(f"images/{self.username}_qr_code.png")
        self.show_chats()

    def show_chats(self):
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
        client.logout(self.username)
        self.username = None
        self.show_login()

    def show_invitations(self):
        self.clear_frame()
        status,invitations = client.get_chat_members(self.username,'invitations')
        tk.Label(self.root, text="Zaproszenia", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text="Wyślij zaproszenie do:", font=("Arial", 12)).pack(pady=(15, 5))
        entry = Entry(self.root, width=30)
        entry.pack(pady=5)
        Button(self.root, text="Wyślij", bootstyle="info", command=lambda: client.invite(self.username,entry.get())).pack(pady=5)
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

    def reply_to_invitation(self,user,decision):
        client.reply_to_invitation(self.username,user,decision)
        self.show_invitations()

    def show_check_chat(self):
        if self.selected_chat.get():
            roommate = (self.selected_chat.get()).split()[-1]
            status,room_code = client.get_room_code(self.username,roommate)
            if status == 200:
                self.current_room_code = room_code
                self.current_roommate = roommate
                self.show_chat()
            else:
                tk.messagebox.showwarning("Brak dostępu do wybranej rozmowy")
        else:
            tk.messagebox.showwarning("Brak wyboru", "Wybierz rozmowę by kontynuować")

    def show_chat(self): 
        self.clear_frame()
        Button(self.root, text="Cofnij", bootstyle="danger", command=self.end_chat).pack(pady=5)
        tk.Label(self.root, text=f"{self.selected_chat.get()}", font=("Arial", 16)).pack(pady=10)
        # Ustal nazwy użytkowników na podstawie wybranej rozmowy
        chat_name = self.selected_chat.get().replace("Rozmowa z ", "")
        self.chat_db = ChatDatabase(self.username, chat_name)
        #pole tekstowe na wiad
        self.chat_box = tk.Text(self.root, height=20, width=45, bg="#f8f9fa", fg="#212529")
        self.chat_box.pack(pady=5)
        # Załaduj wiad z historii
        self.load_chat_history()
        #Pole do wpisywania wiad
        frame = tk.Frame(self.root)
        frame.pack(pady=5)
        self.chat_input = Entry(frame, width=30)
        self.chat_input.pack(side=tk.LEFT, padx=5)
        Button(frame, text="Wyślij", bootstyle="info", command=self.send_message).pack(side=tk.RIGHT, padx=5)
        #self.chat_db.save_message("Hej, to testowa wiadomość od Boba!", "Bob")
        self.load_chat_history()  # Odśwież widok czatu
        self.chat_box.see("end")
        self.root.after(1000,self.get_new_messages)

    def end_chat(self):
        self.current_room_code = None
        self.current_roommate = None
        self.show_chats()

    def load_chat_history(self):
        messages = self.chat_db.get_last_messages(100)
        # Odblokowanie pola
        self.chat_box.config(state="normal")  
        self.chat_box.delete("1.0", tk.END)  # Wyczyść pole tekstowe
        self.chat_box.tag_configure("bold", font=("Arial", 10, "bold"))
        for msg in messages:
            # Dodaj datę (pogrubioną) na osobnej linii
            self.chat_box.insert(tk.END, f"{msg['data']}\n", "bold")
            # Dodaj nazwę użytkownika (pogrubioną) i treść wiadomości (normalna)
            self.chat_box.insert(tk.END, f"{msg['autor']}: ", "bold")
            self.chat_box.insert(tk.END, f"{msg['tresc']}\n\n")  # Wiadomość i odstęp
        # Zablokowanie edycji pola (czat jest tylko do odczytu)
        self.chat_box.config(state="disabled") 

    def get_new_messages(self):
        status,messages = client.get_messages(self.username,self.current_room_code,self.current_roommate)
        if status == 200:
            self.chat_db.save_messages_from_server(messages,self.current_roommate)
            at_bottom = self.chat_box.yview()[1] == 1.0
            if at_bottom:
                self.load_chat_history()
                self.chat_box.see("end")  # Przewiń do ostatniej wiadomości
        self.root.after(1000,self.get_new_messages)

    def send_message(self):
        tresc = self.chat_input.get().strip()
        if not tresc.strip():
            return  # Nie wysyłaj pustych wiadomości
        status = client.send_message(self.username,self.current_room_code,self.current_roommate,tresc)
        if status == 200:
            self.chat_db.save_message(tresc,self.username)  # Zapisz wiadomość
            self.chat_input.delete(0, tk.END)  # Wyczyść pole tekstowe
            self.load_chat_history()  # Odśwież okno czatu
            self.chat_box.see("end")  # Przewiń do ostatniej wiadomości

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()