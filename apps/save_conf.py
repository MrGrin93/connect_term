#!/usr/bin/python3
import rsa
from getpass import getpass, getuser
import requests
import urllib3
import os
import yaml
from netmiko.ssh_dispatcher import ConnectHandler
from netmiko.ssh_exception import NetmikoAuthenticationException, NetmikoTimeoutException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def loginf():
    login = getuser()
    # print(login)
    if os.path.exists(f'/home/{login}/.pswd'):
        with open(f'/home/{login}/.priv', mode='rb') as privatefile:
            keydata = privatefile.read()
            privkey = rsa.PrivateKey.load_pkcs1(keydata)
        with open(f'/home/{login}/.pswd', 'rb') as p:
            encMessage = p.read()
            passw = rsa.decrypt(encMessage, privkey).decode()
    else:
        publicKey, privateKey = rsa.newkeys(512)
        with open(f'/home/{login}/.priv', 'wb') as p:
            pk = rsa.PrivateKey.save_pkcs1(privateKey, format='PEM')
            p.write(pk)
        passw = getpass(prompt='Password:')
        encPassw = rsa.encrypt(passw.encode(),publicKey)
        with open(f'/home/{login}/.pswd', 'wb') as p:
            p.write(encPassw)
    crd = {'usr': login,'pswd': passw}
    # print(crd)
    return crd

def creds(group):
    hashicorp_vault = 'vault.local'
    s = requests.Session()
    data = {"password": loginf()['pswd']}
    result = s.post(f'https://{hashicorp_vault}:8200/v1/auth/ldap/login/{str(loginf()["usr"])}', verify=False, data=data)
    # print(result.json())
    token = result.json()['auth']['client_token']
    vault = requests.Session()
    head={'X-Vault-Token': token}
    pswd = vault.get(f'https://{hashicorp_vault}:8200/v1/network_team_kv/data/{group}', verify=False, headers=head)
    return pswd.json()['data']['data']


def save_config(device):
    
    try:
        with ConnectHandler(**device) as ssh:
            ssh.fast_cli = False
            ssh.enable()
            hn = ssh.find_prompt()
            hn = hn.strip('#')
            
            ssh.send_command('terminal more disable')
            output = ssh.send_command('sh run', expect_string=fr"{hn}#")
            ssh.send_command('terminal more enable')
            
            log_file = open(f'/home/Cisco/confs/{hn}', "w")
            log_file.write(output)
            ssh.disconnect()
        return output
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(error)


with open('/home/ocs/ct_py/cis.yaml') as f:
    devs = yaml.safe_load(f)

for dev in devs:
    devs[dev].update(creds(devs[dev]['group']))
    devs[dev].pop('group')
    print(dev)
    save_config(devs[dev])

with open(f'/home/{getuser()}/.pswd', 'wb') as p:
    p.write('')
