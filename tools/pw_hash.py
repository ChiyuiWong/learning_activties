import base64
import bcrypt
import os

from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.primitives import padding

pw = input("Please enter the password: ")
enc_key = input("Please enter the encryption key in base64: ")
enc_key = base64.b64decode(enc_key)
salt = os.urandom(16)
iv = os.urandom(16)
hashed_pw = bcrypt.kdf(
    password=pw.encode("utf-8"),
    salt=salt,
    desired_key_bytes=32,
    rounds=1000)
cipher = Cipher(algorithms.AES(enc_key), modes.CBC(iv))
encryptor = cipher.encryptor()
padder = padding.PKCS7(128).padder()
padded_plaintext = padder.update(hashed_pw) + padder.finalize()
ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
print(f"Salt: {base64.b64encode(salt)}")
print(f"IV: {base64.b64encode(iv)}")
print(f"Encrypted hash: {base64.b64encode(ciphertext)}")
print(f"Plaintext: {base64.b64encode(hashed_pw)}")
