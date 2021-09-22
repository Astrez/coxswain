from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import os

def getPrivate(path : str = os.path.join(os.getcwd(), 'private_key.pem')):
    try:
        with open(path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        
        return private_key
    except Exception as e:
        raise Exception("Cannot read private key")

def getPublic(path : str = os.path.join(os.getcwd(), 'public_key.pem')):
    try:
        with open(path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        
        return public_key
    except Exception as e:
        raise Exception("Cannot read private key")
