import rsa
import os


def decrypt(crypted, key_root_dir):
    with open(os.path.join(key_root_dir, 'broker_priv.pem'), 'rb') as f:
        priv = f.read()
        privkey = rsa.PrivateKey.load_pkcs1(priv)
        text = rsa.decrypt(crypted, privkey).decode()
        return text

def decrypt_long(crypted, key_root_dir, sep=b'sep'):
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
    text = decrypt(b'\xd79\x07A\x9e>N\xec\x95M\xfa\x7fJm\x84\xcc\xe5\xa0\xb2yw\xa7\xfc\x1c\xa60I2\xe5\xe5\x0cI\x91\xfd}\xdd"\x88P\xe5\xc8c\xae\x0c\x84\xfcB\xa5\x0e\xbf\x93\x84\x15s\x9f\xb9z\xac\x12\xa5\x07\xbd(\xe0t\xa4[\xb8\x86\xa5o\xfd\x03\t\x8e\x9f\xa3\xccC\xca\x81m\xebcEt\x9eT{=`M\xfc-z\x06\x80\xa2\xdaH\xe1o\xed\xbe3\xc6\x1a-h\xb2\xa2(\xa8\xbcPM\x94\n1\x94-\x9c\x1eI\x9d\xec\x93\xaa', ssh_dir)
    print(text)