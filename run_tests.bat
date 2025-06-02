@echo off
pytest tests/test_user_handling.py
pytest tests/test_encryption_management.py
pytest tests/test_logic.py
pytest tests/test_server.py
pytest tests/test_client.py
pause
