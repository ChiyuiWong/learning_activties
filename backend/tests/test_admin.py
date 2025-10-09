import io

import pytest
import pyzipper
from app import create_app

from app.modules.admin.services import AdminService


@pytest.fixture
def app():
    """Create test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_encrypted_zip():
    zip, pw = AdminService.create_encrypted_zip([("a.txt", "hello world"), ("b.txt", "bye world")])
        # Correct pw
    with io.BytesIO(zip) as zip_buffer:
        with pyzipper.AESZipFile(zip_buffer, 'r', encryption=pyzipper.WZ_AES) as zipf:
            zipf.setpassword(pw)
            assert 'a.txt' in zipf.namelist()
            assert 'b.txt' in zipf.namelist()
            assert len(zipf.namelist()) == 2

            # Verify file content
            with zipf.open('a.txt') as f:
                assert f.read().decode('utf-8') == "hello world"
            with zipf.open('b.txt') as f:
                assert f.read().decode('utf-8') == "bye world"
    # Incorrect pw
    zip1, pw1 = AdminService.create_encrypted_zip([("a.txt", "hello world"), ("b.txt", "bye world")])
    # Add 1 to the first byte of the password
    pw1 = bytearray(pw1)
    pw1[0] = (pw1[0] + 1)%256
    pw1 = bytes(pw1)
    with pytest.raises(RuntimeError, match="Bad password for file 'a.txt'"):
        with io.BytesIO(zip1) as zip_buffer:
            with pyzipper.AESZipFile(zip_buffer, 'r', encryption=pyzipper.WZ_AES) as zipf:
                zipf.setpassword(pw1)
                # Verify file content
                with zipf.open('a.txt') as f:
                    f.read().decode('utf-8')
