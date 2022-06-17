#DHCP Configuration Generator
#27/02/2019 written by James Jung
#
#
def mask_len(ip_mask) :
  s = ip_mask.split('.')
  return len(bin(int(s[0])).replace('0b','').replace('0',''))+len(bin(int(s[1])).replace('0b','').replace

('0',''))+len(bin(int(s[2])).replace('0b','').replace('0',''))+len(bin(int(s[3])).replace('0b','').replace('0',''))


def host_ip(host_id):
    ip_l = ip_net.split('.')
    return ip_l[0]+'.'+ip_l[1]+'.'+ip_l[2]+'.'+host_id



def last_host_addr(net_list,mask_list):
   host_ = net_list
   mask_ = mask_list
   if mask_list[2] == '255':
      host_ = net_list
      host_[3] = int(host_[3]) + 253-int(mask_list[3])
      host_[1] = int(host_[1])
      host_[2] = int(host_[2])
      host_[0] = int(host_[0])
      return host_
   elif mask_list[1] == '255':
      host_[2] = int(host_[2]) + 255-int(mask_list[2])
      host_[3] = 253
      host_[1] = int(host_[1])
      host_[0] = int(host_[0])
      return host_
   elif mask_list[0] == '255':
      host_[1] = int(host_[1]) + 255-int(mask_list[1])
      host_[0] = int(host_[0])
      host_[2] = 255
      host_[3] = 253
      return host_


def dhcp_conf_str():
    fname = 'dhcp_'+vlan_name+'.conf'
    last_addr = last_host_addr(net,mask)
    s = '#Wifi Subscribers '+ ip_net +sub_length +'  '+ vlan_name + '\n' + 'subnet ' + ip_net +' netmask ' + ip_mask +'  {\n' + '  range ' + host_ip('20') + ' ' + str(last_addr[0]) + '.' + str(last_addr[1]) + '.' + str(last_addr[2]) + '.' + str(last_addr[3]) + ';\n  option routers ' + host_ip('1') + ';\n  default-lease-time 1800;\n  max-lease-time 1810;\n}\n\n\n### New Subscribers Here ###'
    return s


def dhcp_update(fname, conf_str):
    with open(fname,'r') as file:
       f=file.read()
    if ip_net in f:
       print('\n\nThe subnet is in the range already. Aborting the change...\n\n')
    else:
       ff = f.replace('### New Customer Config Here ###', '\n\n'+conf+'\n')
       with open(fname,'w') as file:
          file.write(ff)


#ip_net='172.31.6.0'
ip_net = raw_input('\nIP Subnet : ')

#ip_mask='255.255.254.0'
ip_mask = raw_input('\nSubnet Mask : ')

#vlan_name='V0374_V0374_LION_Fermentist'
vlan_name = raw_input('\nVLAN Name (ex. V0374_LION_Fermentist): ')

#sub_length_n : integer (23)
sub_length_n = mask_len(ip_mask)

#sub_length : string ('/23')
sub_length ='/'+str(mask_len(ip_mask))

#net = ['172','20','32','0']
net = ip_net.split('.')

#mask = ['255','255','252','0']
mask = ip_mask.split('.')

conf = dhcp_conf_str()

print('\n\n')
print(conf)