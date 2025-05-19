import pytest
import json
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.append(parent_dir)
import client

@pytest.fixture(scope="module",autouse=True)
def cleaning():
    yield
    if os.path.isfile('images/Mirus_qr_code.png'):
        os.remove('images/Mirus_qr_code.png')
    if os.path.exists('data/keys.json'):
        os.remove('data/keys.json')
    if os.path.exists('data/tmp_keys.json'):
        os.remove('data/tmp_keys.json')

def test_register_success(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "token": "dummy_token",
        "secret_key": "JBSWY3DPEHPK3PXP",
        "status": 200
    }
    status = client.register('Mirus','SilneHaslo246@#')
    assert status == 200
    assert os.path.isfile('images/Mirus_qr_code.png')
    os.remove('images/Mirus_qr_code.png')

def test_register_fail(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "status": 400
    }
    status = client.register('Mirus','SilneHaslo246@#')
    assert status == 400
    assert not os.path.isfile('images/Mirus_qr_code.png')

def test_login_success(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "token": "dummy_token",
        "status": 200
    }
    status = client.login('Mirus','SilneHaslo246@#')
    assert status == 200

def test_login_fail(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "status": 400
    }
    status = client.login('Mirus','BledneHaslo')
    assert status == 400

def test_verify_totp_success(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "token": "dummy_token",
        "status": 200
    }
    status = client.verify_totp('Mirus','123456')
    assert status == 200

def test_verify_totp_fail(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "status": 400
    }
    status = client.verify_totp('Mirus','0')
    assert status == 400

def test_invite_success(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "status": 200
    }
    status = client.invite('Mirus','Kobra')
    assert status == 200

def test_invite_fail(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "status": 400
    }
    status = client.invite('Mirus','Yofa')
    assert status == 400

def test_reply_to_invitation_success(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "status": 200
    }
    status = client.reply_to_invitation('Kobra','Mirus','accept')
    assert status == 200

def test_reply_to_invitation_fail(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "status": 400
    }
    status = client.reply_to_invitation('Kobra','Yofa','x')
    assert status == 400

def test_get_chat_members_success(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "users": ["Kobra"],
        "status": 200
    }
    status,users = client.get_chat_members('Mirus','chats')
    assert status == 200
    assert users == ["Kobra"]

def test_get_room_code_success(mocker):
    mock_post = mocker.patch("client.requests.post")
    mock_post.return_value.json.return_value = {
        "room_code": "123456",
        "status": 200
    }
    status,room_code = client.get_room_code('Mirus','Kobra')
    assert status == 200
    assert room_code == "123456"