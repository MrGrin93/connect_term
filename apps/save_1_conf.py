import argparse, urllib3, yaml
from email.policy import default
from netmiko.ssh_dispatcher import ConnectHandler
from netmiko.ssh_exception import NetmikoAuthenticationException, NetmikoTimeoutException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_config(device):
    try:
        with ConnectHandler(**device) as ssh:
            ssh.fast_cli = False
            if device['device_type'] == 'cisco_ios':
                ssh.enable()
            hn = ssh.find_prompt()
            hn = hn.strip('#')
            ssh.send_command('terminal more disable')
            output = ssh.send_command('sh run', expect_string=fr"{hn}#")
            ssh.send_command('terminal more enable')
            log_file = open(f'/usr/local/Cisco/confs/{hn}', "w")
            log_file.write(output)
            ssh.disconnect()
        return output
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print(error)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(dest="dev",  default=None, help='device')
    parser.add_argument(dest="usr",  default=None, help='usr')
    parser.add_argument(dest="passw",  default=None, help='pass')
    parser.add_argument(dest="secret",  default=None, help='pass')
    args = parser.parse_args()

   
    with open('/home/Cisco/cis.yaml') as f:
        devs = yaml.safe_load(f)
    
    host = {'device_type': devs[args.dev]['device_type'],
        'host': devs[args.dev]['host']}

    host['username'] = args.usr
    host['password'] = args.passw
    try:
        host['secret'] = args.secret
    except:
        print('No secret')
    
    save_config(host)
