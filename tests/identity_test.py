# test run: pytest identity_test.py --cov=identity --cov-report=html
import os
import sys

from pytest_mock import MockFixture

sys.path.append('..')
from cipher import *
from identity import *


def test_has_private(mocker: MockFixture):
    id = Identity()
    mocker.patch.object(Identity,'has_private', return_value=True)
    assert id.has_private() is True


def test_load_keys_from_file(mocker: MockFixture) -> None:
    id = Identity()
    mocker.patch.object(Identity,'load_keys_from_file', return_value=id.keys)
    assert id.load_keys_from_file() == id.keys


def test_export_private_key() -> None:
    id = Identity()
    id.export_private_key("export_test")
    assert os.path.exists('.keys/export_test.pem') is True


def test_export_public_key() -> None:
    id = Identity()
    id.export_public_key("export_pub_test")
    assert os.path.exists('.keys/export_pub_test.pub') is True


def test_export_public_key_bytes() -> None:
    id = Identity()
    assert type(id.export_public_key_bytes()) is bytes


def test_get_private_key() -> None:
    id = Identity()
    assert type(id.get_private_key()) is RSA.RsaKey


def test_get_public_key() -> None:
    id = Identity()
    assert type(id.get_public_key()) is RSA.RsaKey


def test_get_keys() -> None:
    id = Identity()
    assert type(id.get_keys()) is dict
    assert type(id.get_keys()['private_key']) is RSA.RsaKey
    assert type(id.get_keys()['public_key']) is RSA.RsaKey


def test_encrypt() -> None:
    id = Identity()
    enc = id.encrypt("test".encode())
    assert type(enc) is tuple
    for msg in enc:
        assert type(msg) is bytes


def test_decrypt() -> None:
    id = Identity()
    data_base64, enc_session_key, tag, nonce = id.encrypt("test".encode())
    dec = id.decrypt(data_base64, enc_session_key, tag, nonce).decode()
    assert type(dec) is str
    assert dec == "test"