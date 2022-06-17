import connect_
import iosCheck_

print("""####

This Script is to configure network devices for new customers.
- Switch(es) configuration : vlan, trunk plumbing
- Subscriber G/W(s) configuration : GW, HSRP, OSPF


The following has not been included in this version.
- Subscriber DHCP configuration
- UCS FI configuration

####"""
#vlanList = iosCheck_.get_Vlans('akmdrwificoresw1')
#print('Currently active VLANs :  \n'.format(vlanList))
vlan_ = raw_input('\nPlease check AKmdrL2WiFiCORESW1 New VLAN ID to use : ')

# Checking if VLAN ID is available
switches = ['akmdrwificoresw1','akmdrwificoresw2', 'akmdrl2wificoresw1', 'akmdrl2wificoresw2', 'akmdrwifiesx01sw']
for ip in switches:
   while iosCheck_.is_Vlan(ip,vlan_):
      print("\nVLAN {0} already exists. Choose another vlan ID(number). ".format(vlan))
      vlan = raw_input('\nVLAN ID : ')

vlanName_ = raw_input('\nVLAN Name(No Space)  : ')
ip_net = raw_input('\nIP Subnet : ')
ip_mask = raw_input('\nSubnet Mask : ')
hsrp_grp_id = raw_input('\nHSRP GROUP ID : ')

# Checking if HSRP GROUP ID is available
grpList = iosCheck_.get_HSRP_GRP('akmdrwifiwsg1')
while hsrp_grp_id in grpList:
  print("\nFollowing Group IDs are currently being used. \n{0}/n/n Choose another GROUP ID(number). ".format(grpList))
  hsrp_grp_id = raw_input('\nHSRP GROUP ID : ')



def host_ip(host_id):
    ip_l = ip_net.split('.')
    return ip_l[0]+'.'+ip_l[1]+'.'+ip_l[2]+'.'+host_id


def sw_conf(child):
    child.sendline('conf t')
    child.sendline('vlan '+vlan_)
    child.sendline('name V0'+vlan_+'_'+vlanName_)
    child.sendline('exit')
    child.sendline('interface po4-5,po21-22,po33-34')
    child.sendline('switchport trunk allowed vlan add '+vlan_)
    child.sendline('end')
    child.sendline('wr')
    child.sendline('exit')
    print('Done...')

def esxsw_conf(child):
    child.sendline('conf t')
    child.sendline('vlan '+vlan_)
    child.sendline('name V0'+vlan_+'_'+vlanName_)
    child.sendline('exit')
    child.sendline('port-profile type ethernet DATA-NX1K-UPLINK')
    child.sendline('switchport trunk allowed vlan add '+vlan_)
    child.sendline('port-profile type vethernet WiFiESX01-TRUNK_WIFI_SUBSCRIBER_DHCP')
    child.sendline('switchport trunk allowed vlan add '+vlan_)
    child.sendline('end')
    child.sendline('wr')
    child.sendline('exit')
    print('Done...')

def wsg_conf(child, hsrpRole):
    child.sendline('conf t')
    child.sendline('interface Po1.'+vlan_)
    child.sendline('description LINK- Spark-WiFi Subscriber VLAN '+vlan_+' '+vlanName_)
    child.sendline('encapsulation dot1Q '+vlan_)
    child.sendline('ip vrf forwarding wifi-subscribers')
    child.sendline('ip address '+gw_ip+' '+ip_mask)
    hsrp_conf(child, hsrpRole)
    child.sendline('service-policy type control V2_SERVICE_POLICY')
    child.sendline('ip subscriber l2-connected')
    child.sendline('initiator unclassified mac-address')
    child.sendline('end')
    child.sendline('wr')
    child.sendline('exit')
    print('Done...')

def hsrp_conf(child, hsrpRole):
    child.sendline('standby '+hsrp_grp_id+' ip '+host_ip('1'))
    if hsrpRole == 1:
       child.sendline('standby '+hsrp_grp_id+' priority 150')
       child.sendline('standby '+hsrp_grp_id+' preempt')
    elif hsrpRole == 2:
       child.sendline('ip ospf cost 20')
    print('HSRP config ...Done...')



#MDR L5 Core Switches
child = connect_.connect('akmdrwificoresw1')
print('Configuring akmdrwificoresw1...')
sw_conf(child)
child.kill
child = connect_.connect('akmdrwificoresw2')
print('Configuring akmdrwificoresw2...')
sw_conf(child)
child.kill

#MDR L2 Core Switches
child = connect_.connect('akmdrl2wificoresw1')
print('Configuring akmdrl2wificoresw1...')
sw_conf(child)
child.kill
child = connect_.connect('akmdrl2wificoresw2')
print('Configuring akmdrl2wificoresw2...')
sw_conf(child)
child.kill

#Nexus 1Kv Switch
child = connect_.connect('akmdrwifiesx01sw')
print('Configuring akmdrwifiesx01sw...')
esxsw_conf(child)
child.kill

#Subscriber Gateway1
gw_ip = host_ip('2')
child = connect_.connect('akmdrwifiwsg1')
print('Configuring akmdrwifiwsg1')
wsg_conf(child, 1)   # 1 : hsrp active
child.kill

#Subscriber Gateway2
gw_ip = host_ip('3')
child = connect_.connect('akmdrwifiwsg2')
wsg_conf(child, 2)  # 2 : hsrp standby
child.kill



#DHCP Server
#child = connect_.connect('aklwsdhcp01')


#UCS System : VLAN, PPLINK, VNIC Template
#child = connect_.connect('10.72.240.68') #L2 UCS FI
#child = pexpect.spawn("ssh -l 'ucs-SparkACS\t806247' 10.72.240.68")
#child.sendline(


#Ruckus Controller

