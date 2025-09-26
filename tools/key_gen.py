import base64
import os
len = int(input("Key length: "))
print(base64.b64encode(os.urandom(len)))