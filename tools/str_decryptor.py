import base64

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

cipher = Cipher(algorithms.AES(base64.b64decode(input("Key in base64: "))),
                modes.CBC(base64.b64decode(input("IV in base64: "))))
decryptor = cipher.decryptor()
padded = decryptor.update(base64.b64decode(input("Ciphertext in base64: "))) + decryptor.finalize()
unpadder = padding.PKCS7(128).unpadder()
plaintext = unpadder.update(padded) + unpadder.finalize()
print(plaintext.decode("UTF-8"))