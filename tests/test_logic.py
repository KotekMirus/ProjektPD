import pytest
import sys
import os
import shutil
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(parent_dir)
import logic as logic

@pytest.fixture()
def db():
    db = logic.ChatDatabase('Mirus','Kobra')
    db._initialize_file()
    yield db
    if os.path.exists('messages'):
        shutil.rmtree('messages')

def test_initialize_file(db):
    assert os.path.exists('messages')
    assert os.path.isfile('messages/Kobra_Mirus.json')

def test_save_and_load(db):
    db.save_message('Cześć','04-05-2025 14:37:28','Kobra')
    db.save_message('Hejo!','05-05-2025 09:13:02','Mirus')
    messages = db.load_messages()
    assert len(messages) == 2
    assert '0' in messages
    assert '1' in messages
    assert messages['0']['tresc'] == 'Cześć'
    assert messages['0']['data'] == '04-05-2025 14:37:28'
    assert messages['0']['autor'] == 'Kobra'
    assert messages['1']['tresc'] == 'Hejo!'
    assert messages['1']['data'] == '05-05-2025 09:13:02'
    assert messages['1']['autor'] == 'Mirus'

def test_save_messages_from_server_and_load(db):
    messages_from_server = [
        ['Cześć!','04-05-2025 08:37:28'],
        ['Co u Ciebie?','04-05-2025 08:45:02'],
        ['Ja gram na PS5','04-05-2025 11:07:53']
    ]
    db.save_messages_from_server(messages_from_server,'Mirus')
    messages = db.load_messages()
    assert len(messages) == 3
    assert '0' in messages
    assert '1' in messages
    assert '2' in messages
    assert messages['0']['tresc'] == 'Cześć!'
    assert messages['0']['data'] == '04-05-2025 08:37:28'
    assert messages['0']['autor'] == 'Mirus'
    assert messages['1']['tresc'] == 'Co u Ciebie?'
    assert messages['1']['data'] == '04-05-2025 08:45:02'
    assert messages['1']['autor'] == 'Mirus'
    assert messages['2']['tresc'] == 'Ja gram na PS5'
    assert messages['2']['data'] == '04-05-2025 11:07:53'
    assert messages['2']['autor'] == 'Mirus'

def test_get_last_messages(db):
    db.save_message('Cześć','04-05-2025 14:37:28','Kobra')
    db.save_message('Hejo!','04-05-2025 14:37:55','Mirus')
    db.save_message('Co u Ciebie?','04-05-2025 14:39:01','Kobra')
    db.save_message('Ja skończyłam Indianę :D','04-05-2025 14:39:16','Kobra')
    db.save_message('Ja dalej ogrywam Obliviona','04-05-2025 14:42:10','Mirus')
    last_messages = db.get_last_messages(3)
    assert len(last_messages) == 3
    assert last_messages[0]['tresc'] == 'Co u Ciebie?'
    assert last_messages[0]['data'] == '04-05-2025 14:39:01'
    assert last_messages[0]['autor'] == 'Kobra'
    assert last_messages[1]['tresc'] == 'Ja skończyłam Indianę :D'
    assert last_messages[1]['data'] == '04-05-2025 14:39:16'
    assert last_messages[1]['autor'] == 'Kobra'
    assert last_messages[2]['tresc'] == 'Ja dalej ogrywam Obliviona'
    assert last_messages[2]['data'] == '04-05-2025 14:42:10'
    assert last_messages[2]['autor'] == 'Mirus'