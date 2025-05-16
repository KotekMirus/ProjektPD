import pytest
import json
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(parent_dir)
import encryption_management as em

@pytest.fixture(scope="module",autouse=True)
def cleaning():
    yield
    if os.path.exists('data/keys.json'):
        os.remove('data/keys.json')
    if os.path.exists('data/tmp_keys.json'):
        os.remove('data/tmp_keys.json')
    if os.path.exists('data'):
        os.rmdir('data')

def test_check_structure_existence():
    em.check_structure_existence()
    assert os.path.exists('data')
    assert os.path.isfile('data/keys.json')
    assert os.path.isfile('data/tmp_keys.json')

def test_asymmetric_encryption_decryption():
    private_key,public_key = em.generate_asymmetric_keys()
    message = "Wiadomość testowa"
    encrypted = em.encrypt_message_asymmetric(public_key,message)
    decrypted = em.decrypt_message_asymmetric(private_key,encrypted)
    assert decrypted == message

def test_symmetric_encryption_decryption():
    key = em.generate_symmetric_key()
    message = "Wiadomość testowa"
    encrypted = em.encrypt_message_symmetric(key,message)
    decrypted = em.decrypt_message_symmetric(key,encrypted)
    assert decrypted == message

def test_save_and_get_key():
    user = "TestUser"
    key = "123456"
    em.save_key(key,user,tmp=False)
    retrieved_key = em.get_key(user,tmp=False)
    assert retrieved_key == key

def test_save_and_get_tmp_key():
    user = "TmpTestUser"
    key = "654321"
    em.save_key(key, user, tmp=True)
    retrieved_key = em.get_key(user, tmp=True)
    assert retrieved_key == key

def test_delete_tmp_key():
    user = "TmpTestUser"
    em.delete_tmp_key(user)
    with open('data/tmp_keys.json', 'r') as file:
        data = json.load(file)
        assert user not in data
