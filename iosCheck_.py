"""
Written by James Jung - 2018.10.31
This script will automate the provision of a new customer on Public WiFi
1. Generate configuration for devices
2. Apply the configurations to the devices
"""

import connect_

def is_Vlan(ip, vlan):
  child = connect_.connect(ip)
  print('Checking {0} ...'.format(ip))
  child.sendline('terminal length 0')
  child.expect('#')
  cmd = 'show vlan id '+str(vlan)
  child.sendline(cmd)
  a = child.expect(['not found','Status'])
  if a == 0:
    child.kill
    return False
  elif a == 1:
    child.kill
    return True


# Need to finish
def get_Vlans(ip):
  child = connect_.connect(ip)
  child.sendline('terminal length 0')
  child.expect('#')
  cmd = 'show vlan brief | in active'
  child.sendline(cmd)
  child.expect('#')
  s = child.before
  vlanList = []

  return vlanList


# return a list of HSRP Group IDs
def get_HSRP_GRP(ip):
  child = connect_.connect(ip)
  child.sendline('!')
  child.expect('#')
  child.sendline('terminal length 0')
  child.expect('#')
  cmd = 'show standby brief'
  child.sendline(cmd)
  child.expect('Virtual IP')
  s = child.buffer
  #print('2... Child Buffer  : \n{0}'.format(child.buffer))
  grpList=[]
  for item in s.splitlines():
    #print(item.split())
    if len(item.split()) >= 2:
       grpList.append(item.split()[1])
  grpList.sort()
  #print('List of GRP IDs  : \n{0}'.format(grpList))
  child.kill
  return grpList


def is_HSRP_GRP(ip,grpID):
  grpList = get_HSRP_GRP(ip)
  if grpID in grpList:
    #print('Returned True')
    return True
  else:
    #print('Returned False')
    print('List of GRP IDs Currently Used :/n       {0}'.format(grpList))
    return False


# Return the lines that has check_string
# Check the string line by line
def checkString(child,command,check_string):
   child.sendline('!')
   child.expect('#')
   child.sendline(command)
   child.expect('#')
   output = child.before.splitlines()
   print(result)
   mStat = False
   match = []
   for item in output:     # check the string line by line
      if check_string in output:
         match.append(item)
   return match



# Check if the string is in the output
def check_stat(child,command,check_string):
   child.sendline('!')
   child.expect('#')
   child.sendline(command)
   child.expect('#')
   result = child.before
   print(result)
   if check_string in result:
      return True
   else:
      return False





def get_run_img(child):
#"""
#Return running ios image file name of the cisco ios device
#"""
   try:
      child.sendline('show version')
      child.expect('Last reload')
      for item in child.before.split():
          #print(item)
          if '.bin' in item:
             run_img = item[7:-1]
             print('Check Point 1.1 : Running img : ', run_img)
             #input('Enter 1 :')
             #if ( run_img == target_img ):
             #         print(ip,'   #### Running Img : ',run_img,'   This Device is UP To DATE!!!  ###')
             #         child.sendline(' ')
             #        child.sendline(' ')
             #         child.sendline(' ')

             break
      return run_img
   except:
      raise




def flash_img(child,cur_img):
#"""
#Return a list of ios images on the flash of the device
#"""
   try:
      child.sendline(' ')
      child.expect('#')
      child.setecho(False)
      child.sendline('show flash:')
      ji = child.expect(['free','used','No space info'],timeout=15)
      if ji == 2:
        return  'None'
      else:
         #print(ip, '       child.before  =  ',child.before,'     child.match =            ',child.match,'               child.after =        ',child.after)
         _i = 0
         for item in child.before.splitlines():
             if '.bin' in item:
                cur_img[_i] = item.split()[-1]
                print(ip, '   Current Image in Flash : ',cur_img)
                _i += 1
         #input('Enter 1:')
         return cur_img;
   except:
      raise

def flash_free(child,free_space):
#"""
#Return free space of the flash drive of the device
#"""
   try:
      child.sendline(' ')
      child.expect('#')
      child.sendline('show flash')
      _e = child.expect(['free','used'],timeout=15)
      cb = child.before.splitlines()
      print(ip,'  -e  =     ',_e)
      print(ip, cb)
      #print('       child.before  =  ',child.before,'     child.match =            ',child.match,'               child.after =        ',child.after)
      #if _e == 0:
      #if 'free' in child.after:
      if _e == 0:
         for item in cb:
             if 'total' in item:
                free_space = item.split()[3][1:]
                print(ip,'   Free Space : ',free_space)
         return free_space
      elif _e == 1:
         for item in cb:
             if 'available' in item:
                free_space = item.split()[0]
                print(ip,'   Free Space : ',free_space)
         return free_space
      else:
         free_space = 10
         return free_space
   except:
      raise



