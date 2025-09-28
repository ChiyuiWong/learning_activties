import base64
import datetime

from config.database import get_db_connection
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dotenv import load_dotenv
import json
load_dotenv()

class ActionLogger:
    def __init__(self, module: str):
        self.module = module
    def log(self, username: str, ip_address: str, msg: str):
        # The extra created_at is intentionally added to create a way to cross-check against replay attack.
        data = json.dumps({"username": username, "ip_address": ip_address, "msg": msg, "created_at": str(datetime.datetime.now())})
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(base64.b64decode(os.environ.get("ACTION_LOG_ENC_KEY"))), modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_plaintext = padder.update(data.encode("utf-8")) + padder.finalize()
        encrypted_data = encryptor.update(padded_plaintext) + encryptor.finalize()
        with get_db_connection() as client:
            db = client['comp5241_g10']
            db["action_log"].insert_one(
                {
                 "module": self.module,
                 "encrypted_data": encrypted_data,
                 "encryption_iv": iv,
                 "created_at": datetime.datetime.now(datetime.UTC),
                })
