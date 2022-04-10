# connect_term
for ssh connection to devices from inventory file
usage: ct [-h] [-l] [-L] [-C command list [command list ...]] [-t file path] [-R] host

positional arguments:
  host                  hostname

optional arguments:
  -h, --help            show this help message and exit
  -l                    locac user of cisco device
  -L                    open interactive session with ssh
  -C command list [command list ...]
                        send list of commands in '' and sep ','
  -t file path          send config from file
  -R                    save sh run in file
  
  ct.copy1 do same things, but save password in home directory of user and ecrypt it with rsa key
  
  
save_confs save running config from cisco devices
will make user with privelege to make just sh run to shedule this script


Upload send access lists (may do somethig else) to deices

 
