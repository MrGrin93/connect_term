import re
import yaml

acl_ptrn = (
    r'^ip\saccess-list\sextended\s(\S+)\n(^\s.+\n){0,}'
)

cors = ['sw1', 'sw2', 'sw3', 'sw4']
c = 0
for cor in cors:
    with open(f'/usr/local/Cisco/confs/{cor}') as file:
        data = file.read()
        # print(data)
        with open('/tftp/tftpboot/ACL_SECURITY/acl_devs.yaml', 'r') as ac:
            acls = yaml.safe_load(ac)
        # find all matches in the data
        match_all = re.finditer(acl_ptrn, data, re.MULTILINE)
        for match in match_all:
            if match.group(1) in acls:
                # print(match.group(1))
                with open(f'/home/Cisco/acl/{match.group(1)}', 'w') as file:
                    begin = f'interface {match.group(1).split("_")[0]}\n no ip access-group {match.group(1)} {match.group(1).split("_")[-1]}\nno ip access-list extended {match.group(1)}\n'
                    end = f'interface {match.group(1).split("_")[0]}\n ip access-group {match.group(1)} {match.group(1).split("_")[-1]}\nend'
                    result = f'{begin}\n{match.group(0)}{end}'
                    file.write(result)
                c += 1
print(c)