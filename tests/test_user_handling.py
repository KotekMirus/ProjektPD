import pytest
import pyotp
import json
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(parent_dir)
import user_handling as uh

@pytest.fixture(scope="function",autouse=True)
def cleanup():
    yield
    if os.path.exists('data/users.json'):
        os.remove('data/users.json')
    if os.path.exists('data'):
        os.rmdir('data')

def test_check_structure_existence():
    user = uh.user('Mirus','SilneHaslo246@#')
    user.check_structure_existence()
    assert os.path.exists('data')
    assert os.path.isfile('data/users.json')

def test_register_and_save():
    user1 = uh.user('Mirus','SilneHaslo246@#')
    assert user1.register() == True
    user2 = uh.user('Mirus','SilneHaslo246@#')
    assert user2.register() == False
    user3 = uh.user('Mirus','InneHaslo246@#!')
    assert user3.register() == False
    users = None
    with open('data/users.json','r') as file:
        users = json.load(file)
    assert 'Mirus' in list(users.keys())

def test_verify():
    user1 = uh.user('Mirus','SilneHaslo246@#')
    user1.register()
    assert user1.verify() == True
    user2 = uh.user('Mirus','InneHaslo246@#!')
    assert user2.verify() == False
    user3 = uh.user('Kobra','SilneHaslo123@#')
    assert user3.verify() == False

def test_verify_totp():
    user = uh.user('Mirus','SilneHaslo246@#')
    user.register()
    secret = None
    with open('data/users.json','r') as file:
        users = json.load(file)
        secret = users['Mirus']['secret_key']
    totp = pyotp.TOTP(secret)
    assert user.verify_totp('0') == False
    assert user.verify_totp(totp.now()) == True

def test_add_to_pending_room():
    user1 = uh.user('Mirus','SilneHaslo246@#')
    user1.register()
    user2 = uh.user('Kobra','SilneHaslo123@#')
    user2.register()
    user1.add_to_pending_room('456123','Kobra','klucz')
    users = None
    with open('data/users.json','r') as file:
        users = json.load(file)
    assert ['456123','klucz'] in users['Mirus']['pending_rooms']
    assert ['456123','klucz'] in users['Kobra']['pending_rooms']

def test_get_room_codes():
    user1 = uh.user('Mirus','SilneHaslo246@#')
    user1.register()
    user2 = uh.user('Kobra','SilneHaslo123@#')
    user2.register()
    user3 = uh.user('Wiercik','SilneHaslo789@#')
    user3.register()
    user1.add_to_pending_room('456123','Kobra','klucz')
    user1.add_to_pending_room('246802','Wiercik','klucz')
    accepted,pending = user1.get_room_codes()
    assert not accepted
    assert '456123' in pending and '246802' in pending