from ciscoconfparse import CiscoConfParse
import yaml
from ipaddress import *

def parse (file):
    parse = CiscoConfParse(file, syntax='ios')

    
    global_obj = parse.find_objects(r'^hostname')
    hostname = global_obj[0].re_match_typed(r'^hostname\s+(\S+)', default='')

    vlans={hostname:[]}

    for intf_obj in parse.find_objects('^interface'):

        int_name = intf_obj.re_match_typed('^interface\s+(\S.+?)$')

        int_ip = intf_obj.re_match_iter_typed(
            r'ip\saddress\s(\d+\.\d+\.\d+\.\d+)\s(\d+\.\d+\.\d+\.\d+)$', result_type=str,
            group=1, default='Empty')

        int_mask = intf_obj.re_match_iter_typed(
            r'ip\saddress\s(\d+\.\d+\.\d+\.\d+)\s(\d+\.\d+\.\d+\.\d+)$', result_type=str,
            group=2, default='')
        
        int_ip_sec = intf_obj.re_match_iter_typed(
            r'ip\saddress\s(\d+\.\d+\.\d+\.\d+)\s(\d+\.\d+\.\d+\.\d+)\ssecondary', result_type=str,
            group=1, default='')
        
        int_mask_sec = intf_obj.re_match_iter_typed(
            r'ip\saddress\s(\d+\.\d+\.\d+\.\d+)\s(\d+\.\d+\.\d+\.\d+)\ssecondary', result_type=str,
            group=2, default='')

        int_shut =  intf_obj.re_match_iter_typed(
            r'shutdown', result_type=str,
            group=0, default='active')
        
        int_desc = intf_obj.re_match_iter_typed(
            r'description\s(.+)$', result_type=str,
            group=1, default='')
        
        int_acl_in = intf_obj.re_match_iter_typed(
            r'access-group\s(\S+)\sin', result_type=str,
            group=1, default='')

        int_acl_out = intf_obj.re_match_iter_typed(
            r'access-group\s(\S+)\sout', result_type=str,
            group=1, default='')

        if int_desc == '':
            int_desc = int_name
        
        if int_mask != '':
            int_mask = IPv4Network(f'0.0.0.0/{int_mask}').prefixlen

        if int_mask_sec != '':
            int_mask_sec = IPv4Network(f'0.0.0.0/{int_mask_sec}').prefixlen

        
        vlan = {'int':int_name, 'ip': int_ip, 'mask': int_mask , 'ip_sec': int_ip_sec, 'mask_sec': int_mask_sec ,'desc': int_desc, 'acl_in': int_acl_in, 'acl_out': int_acl_out, 'status': int_shut}
        vlans[hostname].append(vlan)
    return vlans

acl_devs = {}

cors = ['sw1', 'sw2', 'sw3', 'sw4']
for cor in cors:

    cisco_data = parse(f'/Cisco/confs/{cor}')

   
    for vlan in cisco_data[cor]:
        # print(vlan['int'])
        if vlan['acl_in'] != '' and vlan['acl_in'] not in acl_devs:
            acl_devs[vlan['acl_in']] = []
        if vlan['acl_in'] != '' and cor not in acl_devs[vlan['acl_in']]:
            acl_devs[vlan['acl_in']].append(cor)
        if vlan['acl_out'] != '' and vlan['acl_out'] not in acl_devs:
            acl_devs[vlan['acl_out']] = []
        if vlan['acl_out'] != '' and cor not in acl_devs[vlan['acl_out']]:
            acl_devs[vlan['acl_out']].append(cor)


# acl_devs to yaml file
with open('/home/Cisco/acl_devs.yaml', 'w') as f:
    yaml.dump(acl_devs, f, default_flow_style=False)

