@echo off
set "BASE_DIR=%~dp0"
set "EVERYTHING_DIR=%BASE_DIR%all"
mkdir "%EVERYTHING_DIR%"
for %%X in (server user1 user2) do (
    mkdir "%EVERYTHING_DIR%\%%X\images"
    copy "%BASE_DIR%images\ikona.ico" "%EVERYTHING_DIR%\%%X\images\ikona.ico"
    copy "%BASE_DIR%key.txt" "%EVERYTHING_DIR%\%%X\key.txt"
)
start cmd /k "cd /d %EVERYTHING_DIR%\server && python ..\..\main.py server"
start cmd /k "cd /d %EVERYTHING_DIR%\user1 && python ..\..\main.py client"
start cmd /k "cd /d %EVERYTHING_DIR%\user2 && python ..\..\main.py client"
