import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Entry, Button, Checkbutton
from logic import ChatDatabase
import time
from tkinter import messagebox
from PIL import Image, ImageTk


class Chattersi:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("Chattersi")
        self.root.geometry("400x550")
        self.style = Style("solar")
        self.selected_chat = tk.StringVar()
        self.root.iconbitmap('images/ikona.ico')

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

        Button(self.root, text="Zaloguj", bootstyle="info", command=self.show_totp).pack(pady=5)
        Button(self.root, text="Zarejestruj", bootstyle="success", command=self.show_register).pack(pady=5)
    
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

        Button(self.root, text="Zarejestruj", bootstyle="success", command=self.show_qr).pack(pady=5)
        Button(self.root, text="Wróć", bootstyle="warning", command=self.show_login).pack(pady=5)
    
    def show_totp(self):
        self.clear_frame()
        tk.Label(self.root, text="Podaj TOTP", font=("Arial", 16)).pack(pady=10)

        entry = tk.Entry(self.root, width=30, fg="gray")
        entry.insert(0, "Kod TOTP")
        entry.bind("<FocusIn>", lambda e: entry.delete(0, tk.END) if entry.get() == "Kod TOTP" else None)
        entry.bind("<FocusOut>", lambda e: entry.insert(0, "Kod TOTP") if entry.get() == "" else None)
        entry.pack(pady=5, ipady=5)

        Button(self.root, text="Zweryfikuj", bootstyle="info", command=self.show_chats).pack(pady=5)
        #Button(self.root, text="Cofnij", bootstyle="danger", command=self.show_login).pack(pady=5)

    def show_qr(self):
        self.clear_frame()
        tk.Label(self.root, text="Zeskanuj kod QR", font=("Arial", 16)).pack(pady=10)
        #tk.Label(self.root, text="TU WYSWIETLI SIE KOD", font=("Arial", 16)).pack(pady=10)

        image = Image.open("images/Kobra_qr_code.png")
        self.qr_img = ImageTk.PhotoImage(image)  # Musi być przypisane do self, by nie zostało usunięte z pamięci

        tk.Label(self.root, image=self.qr_img).pack(pady=10)

        tk.Label(self.root, text="Zeskanuj kod QR za pomocą aplikacji uwierzytelniającej na swoim telefonie, następnie naciśnij przycisk Dalej", font=("Arial", 11), wraplength=250).pack(pady=10)

        Button(self.root, text="Dalej", bootstyle="info", command=self.show_chats).pack(pady=5)
        #Button(self.root, text="Cofnij", bootstyle="danger", command=self.show_login).pack(pady=5)

    def show_chats(self):
        self.clear_frame()
        tk.Label(self.root, text="Wybierz rozmowę", font=("Arial", 16)).pack(pady=10)
        
        conversations = ["Rozmowa z Alicją", "Rozmowa z Bobem"]
        for conv in conversations:
            frame = tk.Frame(self.root, bg="#d9edf7", bd=2, relief=tk.RIDGE)
            frame.pack(fill=tk.X, padx=20, pady=5)
            radio = tk.Radiobutton(frame, text=conv, variable=self.selected_chat, value=conv, font=("Arial", 12), bg="#d9edf7", anchor='w')
            radio.pack(padx=10, pady=10, anchor='w')
        
        Button(self.root, text="Przejdź", bootstyle="info", command=self.show_check_chat).pack(pady=5)
        Button(self.root, text="Zaproszenia", bootstyle="success", command=self.show_invitations).pack(pady=5)
        Button(self.root, text="Wyloguj", bootstyle="danger", command=self.show_login).pack(pady=5)

    def show_invitations(self):
        self.clear_frame()
        tk.Label(self.root, text="Zaproszenia", font=("Arial", 16)).pack(pady=10)

        # Przykładowe zaproszenia
        invitations = ["Alicja", "Tomek"]

        for user in invitations:
            frame = tk.Frame(self.root, bd=1, relief=tk.RIDGE, padx=10, pady=5)
            frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(frame, text=f"Zaproszenie od: {user}", font=("Arial", 12)).pack(side=tk.LEFT)

            btn_frame = tk.Frame(frame)
            btn_frame.pack(side=tk.RIGHT)

            Button(btn_frame, text="Akceptuj", bootstyle="success").pack(side=tk.LEFT, padx=5)
            Button(btn_frame, text="Odrzuć", bootstyle="danger").pack(side=tk.LEFT, padx=5)

        # Formularz do wysyłania zaproszenia
        tk.Label(self.root, text="Wyślij zaproszenie do:", font=("Arial", 12)).pack(pady=(15, 5))
        entry = Entry(self.root, width=30)
        entry.pack(pady=5)
        Button(self.root, text="Wyślij", bootstyle="info").pack(pady=5)

        Button(self.root, text="Wróć", bootstyle="secondary", command=self.show_chats).pack(pady=15)


    def show_check_chat(self):
        if self.selected_chat.get():
            self.show_chat()
        else:
            tk.messagebox.showwarning("Brak wyboru", "Wybierz rozmowę by kontynuować")

    def show_chat(self):
        self.clear_frame()
        Button(self.root, text="Cofnij", bootstyle="danger", command=self.show_chats).pack(pady=5)
        tk.Label(self.root, text=f"{self.selected_chat.get()}", font=("Arial", 16)).pack(pady=10)
        
        # Ustal nazwy użytkowników na podstawie wybranej rozmowy
        chat_name = self.selected_chat.get().replace("Rozmowa z ", "")
        self.chat_db = ChatDatabase("AktualnyUżytkownik", chat_name)

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
    
        """self.chat_db.save_message("Hej, to testowa wiadomość od Boba!", "Bob")"""
        self.load_chat_history()  # Odśwież widok czatu

        
    def load_chat_history(self):
        messages = self.chat_db.get_last_messages(10)

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

        self.chat_box.see("end")  # Przewiń do ostatniej wiadomości

    def send_message(self):
        tresc = self.chat_input.get().strip()
        if not tresc.strip():
            return  # Nie wysyłaj pustych wiadomości

        self.chat_db.save_message(tresc, "AktualnyUżytkownik")  # Zapisz wiadomość
        self.chat_input.delete(0, tk.END)  # Wyczyść pole tekstowe
        self.load_chat_history()  # Odśwież okno czatu

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()


    def run(self):
        self.root.mainloop()

