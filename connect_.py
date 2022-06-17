"""
Last Update 2018.11.02
Written and Updated by James Jung
Cisco IOS Module
"""
#import os
#import sys
import pexpect
#import subprocess
import time
#import logging
#import re
#import threading
#Credentials
creds = [('automate','aut0m@t3'),('admin','pr0dr1v3'),('admin','Ph0n3box'),('connectcore','WB=iE0g#.u*HuMMZ;;Cxp')]
pwl = []
for y in creds:
   pwl.append(y)




def enable(child):
#"""
#Get into the enable mode of the device.
#child is a pointer to pexpect.spawn().
#"""
    try:
       i = child.expect(['#','>','login','assword:'])
       if i == 0:
          #print("Haha")
          child.sendline('')
          return True
       elif i == 1:
          child.sendline('enable')
          child.expect('assword:')
          child.sendline(switch_pw)
          j = child.expect(['#','assword:'])
          if j == 0:
             return True
          else:
             child.sendcontrol('c')
             child.sendcontrol('c')
             print(ip, '\nCheck the device. Can\'t go into Enable mode.')
             return False
       elif i == 2:
          child.sendline(switch_un)
          child.expect('assword:')
          child.sendline(switch_pw)
          j = child.expect(['#','assword:'])
          if j == 0:
             return True
          else:
             child.sendcontrol('c')
             child.sendcontrol('c')
             print(ip, '\nCheck the device. Can\'t go into Enable mode.')
             return False
       elif i == 3:
          child.sendline(switch_pw)
          j = child.expect(['#','assword:'])
          if j == 0:
             return True
          elif j == 1:
             child.sendcontrol('c')
             for (a,b) in creds:
                connect_SW(a,ip)


          else:
             child.sendline('c')
             child.sendline('c')
             print(ip, '\nCheck the device. Can\'t go into Enable mode.')
             return False
       else:
          return False
    except:
       raise




# Need to improve
def tryPass(child,pw):
  try:
      child.sendline('enable')
      child.expect('assword')
      pwl.remove(pw)
      while pwl != []:
         child.sendline(pw)
         a = child.expect(['#','assword'])
         if a == 0:    # Enable Mode
            return True
         elif a == 1:  # Wrong password. Try another password
            pw = pwl.pop()   #
         else:
            # If there's any other case
            print('Password does not work !!!')

      return False
  except:
    raise


def sudo_(child,pw):
  try:
     child.sendline('sudo su -')
     child.expect('assword')
     child.sendline(pw)
     response_ = child.expect(['#'])
  except:
    raise



def connect(ip):
#
  try:
    for u,p in creds:
      if ip == '10.72.240.68':  # UCS FI
         child = pexpect.spawn("ssh -l 'ucs-SparkACS\%s' %s" % (u,ip), maxread=200000, searchwindowsize=200000)
      else:
         child = pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' % (u,ip), maxread=200000, searchwindowsize=200000)
      child.delaybeforesend = 1
      child.expect('assword:')
      child.sendline(p)
      a = child.expect(['assword','>','#','login','Are you sure you want to continue connecting (yes/no)?',pexpect.TIMEOUT,pexpect.EOF,'Connection refused','Connection timed out','Connection refused by server'])
      if a == 0:    #login again - go to for loop
          pass
      elif a == 1:  #  '>' user mode
          if enable(child):
             child.sendline('!')
             return child
      elif a == 2:  #   '#' Enable mode
          child.sendline('!')
          return child
      elif a == 3:  # Username required
          child.sendline(u)
          child.expect('assword:')
          child.sendline(p)
          if enable(child,p):
              child.sendline('!')
              return child
          else:
              print('\n\n{0} Failed to go into Enable Mode\n\n'.format(ip))
              return child
      elif a == 4:
           child.sendline('yes')
           enable(child)
      elif a == 7 or a == 9:
           print('Connection Refused ...')
      else:
           print('Connection Timeout ....')
  except:
     raise






def ssh_connect(ip,os='ios'):
        try:
                print('\n\n')
                print(ip,'   Trying a remote device ..')
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' % (switch_un, ip),maxread=10000)
                child.delaybeforesend = 1
                #child.logfile = logfiler(ip)
                child.timeout = 6000
                cur_img = ['a','a','a','a']
                i = child.expect(['Password:',pexpect.TIMEOUT,pexpect.EOF,'Connection refused','Connection timed out','Connection refused by server','Are you sure you want to continue connecting (yes/no)?'])
                if i == 0:
                        child.sendline(switch_pw)
                        if(enable(child)):
                           #print("In Enable Mode")
                           child.sendline('terminal length 0')
                           child.expect('#')
                           fi = flash_img(child,cur_img)
                           print(ip,'Current Img on Flash :   ',fi)
                           if target_img in fi:
                              print(ip, 'Target img is already in Flash Drive')
                           elif fi == 'None':
                              child.sendline('!')
                              print(ip, 'Error opening flash: ... No space information available')
                           else:
                              fs = flash_free(child,free_space)
                              print(ip,'Free Space in Falsh :   ',fs)
                              ri = running_img(child,run_img)
                              print(ip,'Running Imgage :  ',ri)
                              Upload(child,ri,fi,fs)
                        else:
                           print(ip, 'Can\'t get into enable mode')
                        #child.sendline('end')
                        #child.expect('#')
                        #child.sendline('wr mem')
                        #child.expect('[OK]')
                        child.sendline('!')
                        child.expect('#')
                        child.sendline('quit')
                        logger.info( '%s : Operation Succssful !!!', ip)
                        print('%s : Operation Successful !!!  -o_0-' % ip)
                        sys.exit
                elif i == 1:
                        logger.info('%s : Timeout', ip)
                        print('\n\n%s : Timeout'% ip)
                        sys.exit
                elif i == 2:
                        logger.info('%s : Reached EOF', ip)
                        print('\n\n%s : Reached EOF'% ip)
                        sys.exit
                elif i == 3:
                        logger.info('%s : Connection refused', ip)
                        print('\n\n%s : Connection refused'% ip)
                        sys.exit
                elif i == 4:
                        logger.info('%s : Connection Timed Out', ip)
                        print('\n\n%s : Connection Timed Out'% ip)
                        sys.exit
                elif i == 5:
                        logger.info('%s : Connection refused by server', ip)
                        print('\n\n%s : Connection refused by server' % ip)
                        sys.exit
                elif i == 6:
                        child.sendline('yes')
                        enable(child)
                        Upgrade(child)
                        #child.sendline('end')
                        child.expect('#')
                        #child.sendline('wr mem')
                        #child.expect('[OK]')
                        #child.expect('#')
                        child.sendline('quit')
                        logger.info( '%s : Operation Succssful !!!', ip)
                        print('%s : Operation Successful !!!  -o_0-' % ip)
                        sys.exit

                child.logfile.close()

        except:
                raise

