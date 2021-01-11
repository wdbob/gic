import rsa
import os

def create_keys(key_root_dir):
    (pubkey, privkey) = rsa.newkeys(2048)
    pub = pubkey.save_pkcs1()
    with open(os.path.join(key_root_dir, 'broker_pub.pem'), 'wb+') as f:
        f.write(pub)
    priv = privkey.save_pkcs1()
    with open(os.path.join(key_root_dir, 'broker_priv.pem'), 'wb+') as f:
        f.write(priv)


if __name__ == "__main__":
    home = os.path.expanduser('~')
    ssh_dir = os.path.join(home, '.ssh')
    create_keys(ssh_dir)
