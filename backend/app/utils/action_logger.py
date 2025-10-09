import base64
import datetime
import os
import json
from typing import Optional

from flask import current_app
from config.database import get_db_connection
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class ActionLogger:
    def __init__(self, module: str):
        self.module = module

    def _get_action_key(self) -> Optional[bytes]:
        # Prefer Flask config when running inside an app context (tests set TestConfig.ACTION_LOG_ENC_KEY)
        try:
            if current_app and 'ACTION_LOG_ENC_KEY' in current_app.config:
                key_b64 = current_app.config.get('ACTION_LOG_ENC_KEY')
            else:
                key_b64 = os.environ.get('ACTION_LOG_ENC_KEY')
        except RuntimeError:
            # Not in an app context
            key_b64 = os.environ.get('ACTION_LOG_ENC_KEY')

        if not key_b64:
            return None

        # Accept already-bytes or a base64-encoded string
        if isinstance(key_b64, (bytes, bytearray)):
            return bytes(key_b64)
        try:
            return base64.b64decode(key_b64)
        except Exception:
            return None

    def log(self, username: str, ip_address: str, msg: str):
        # The extra created_at is intentionally added to create a way to cross-check against replay attack.
        data = json.dumps({
            "username": username,
            "ip_address": ip_address,
            "msg": msg,
            "created_at": str(datetime.datetime.now()),
        })

        key = self._get_action_key()
        iv = os.urandom(16)

        if key is None:
            # If no key available, skip encryption and store plaintext for tests/dev only
            encrypted_data = data.encode('utf-8')
            encryption_iv = None
        else:
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()
            padded_plaintext = padder.update(data.encode("utf-8")) + padder.finalize()
            encrypted_data = encryptor.update(padded_plaintext) + encryptor.finalize()
            encryption_iv = iv

        with get_db_connection() as client:
            # Prefer an explicit DB name from Flask config when available; fall back to default
            try:
                db_name = None
                if current_app:
                    db_name = current_app.config.get('MONGODB_DB') or current_app.config.get('MONGODB_TEST_DB')
            except RuntimeError:
                db_name = None

            if not db_name:
                db_name = os.environ.get('MONGODB_DB', 'comp5241_g10')

            db = client[db_name]
            db["action_log"].insert_one(
                {
                    "module": self.module,
                    "encrypted_data": encrypted_data,
                    "encryption_iv": encryption_iv,
                    "created_at": datetime.datetime.now(datetime.timezone.utc),
                }
            )
