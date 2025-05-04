import server
import GUI
import sys

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'server':
        server.run_server()
    elif mode == 'client':
        client_window = GUI.Chattersi()
        client_window.run()
    else:
        print("Wprowadzono nieprawidłową nazwę trybu pracy. Dostępne tryby pracy to 'server' oraz 'client'.")