# ProjektPD
Projekt na studia drugiego stopnia. Przedmiot: Programowanie defensywne.  
Temat: Bezpieczny komunikator internetowy "Chattersi".

### Uruchamianie:  
Windows:  
Aby uruchomić aplikację, należy skorzystać z pliku run.bat. Skrypt ten automatycznie tworzy folder all, odtwarza wymaganą strukturę katalogów oraz umieszcza tam dane serwera oraz obu użytkowników.  
Pozostałe systemy operacyjne:  
Aby uruchomić aplikację, należy utworzyć dwa lub więcej folderów i do wszystkich przekopiować zawartość głównego katalogu projektu. W jednym z folderów należy otworzyć terminal i wykonać komendę python main.py server. W pozostałych folderach należy otworzyć terminal i wykonać komendę python main.py client. Zostaną odpowiednio uruchomione serwer i wybrana liczba klientów.

### Testowanie:  
Windows:  
Aby uruchomić testy, należy skorzystać z pliku run_tests.bat. Skrypt ten automatycznie tworzy niezbędne zasoby w katalogach data oraz images, przeprowadza testy, a następnie usuwa dane tymczasowe wygenerowane w trakcie testów.  
Pozostałe systemy operacyjne:  
Aby uruchomić test, należy otworzyć terminal w głównym katalogu projektu i wykonać komendę pytest tests/X, gdzie X to nazwa dowolnego pliku z folderu tests.

### Dokumentacja:  
Windows:  
Aby otworzyć dokumentację, należy skorzystać z pliku open_docs.bat. Skrypt ten otworzy startowy plik html w domyślnej przeglądarce.  
Pozostałe systemy operacyjne:  
Aby otworzyć dokumentację, należy otworzyć plik index.html w dowolnej przeglądarce. Plik ten znajduje się w docs\html\index.html.

### Uwaga!  
* Przed korzystaniem z projektu należy zainstalować wymagane moduły poprzez wykonanie w terminalu pip install -r requirements.txt w lokalizacji głównego katalogu projektu.
* Testy są wrażliwe na strukturę ścieżek, dlatego nie należy uruchamiać ich ręcznie z przypadkowych lokalizacji. Zaleca się korzystanie wyłącznie z dostarczonego skryptu run_tests.bat lub postępowanie zgodnie z zapewnioną instrukcją.
* Projekt powstał na wersji Python 3.11.9.