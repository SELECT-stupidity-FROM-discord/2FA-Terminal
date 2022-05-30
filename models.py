import os
import base64
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes


SALT = b'KWJUEGJGRIOJHIOJHIOTIHONET'

if not os.path.exists('./database/'):
    os.mkdir('./database/')

class AESCipher:
    def __init__(self, password: str) -> None:
        self.__key__ = hashlib.sha256(password.encode('utf-8') + SALT).digest()

    def encrypt(self, raw):
        BS = AES.block_size
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

        raw = base64.b64encode(pad(raw).encode('utf8'))
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key=self.__key__, mode= AES.MODE_CFB,iv=iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        unpad = lambda s: s[:-ord(s[-1:])]
        enc = base64.b64decode(enc)

        iv = enc[:AES.block_size]
        cipher = AES.new(self.__key__, AES.MODE_CFB, iv)
        return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf8'))