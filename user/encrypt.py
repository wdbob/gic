import os
import rsa
import json


def encrypt(text, key_root_dir):
    with open(os.path.join(key_root_dir, 'broker_pub.pem'), 'rb') as f:
        pub = f.read()
        pubkey = rsa.PublicKey.load_pkcs1(pub)
        text = text.encode()
        crypted = rsa.encrypt(text, pubkey)
        return crypted

def encrypt_long(text, key_root_dir, length=100, sep=b'sep'):
    with open(os.path.join(key_root_dir, 'broker_pub.pem'), 'rb') as f:
        pub = f.read()
        pubkey = rsa.PublicKey.load_pkcs1(pub)
        text = text.encode()
        n = int(len(text)/length)
        crypted = b''
        cnt = 0
        for i in range(n):
            tmp = text[i*length:(i+1)*length]
            tmp = rsa.encrypt(tmp, pubkey)
            crypted += tmp
            crypted += sep
            cnt += 1
        tmp = text[cnt*length:]
        tmp = rsa.encrypt(tmp, pubkey)
        crypted += tmp
        return crypted

def decrypt_long(crypted, key_root_dir, length=100, sep=b'sep'):
    with open(os.path.join(key_root_dir, 'broker_priv.pem'), 'rb') as f:
        priv = f.read()
        privkey = rsa.PrivateKey.load_pkcs1(priv)
        crypted = crypted.split(sep)
        text = ''
        for c in crypted:
            tmp = rsa.decrypt(c, privkey).decode()
            text += tmp
        return text

if __name__ == "__main__":
    home = os.path.expanduser('~')
    ssh_dir = os.path.join(home, '.ssh')
    msg = {
        'text': 'just a test'
    }
    msg = json.dumps(msg)
    crypted = encrypt_long(msg, ssh_dir)
    print(str(crypted).encode())
    print('-----')
    text = decrypt_long(crypted, os.path.join(ssh_dir, 'gic'))
    text = json.loads(text)
    print(len(crypted), crypted)
    print(text)

