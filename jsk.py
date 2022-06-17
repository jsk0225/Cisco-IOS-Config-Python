"""
Last Update 2018.10.31
Written and Updated by James Jung
Cisco IOS Module
"""
import os
import sys
import pexpect
import subprocess
import time
import logging
import re
import threading

#Switch username
switch_un = "t806247"
#Switch password
switch_pw = "summer16"
#Credentials
creds = [('admin','Ph0n3box')]

def connect_SW(switch_un,ip='akmdrl2wificoresw1'):
  child = pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' % (switch_un,ip))
  if enable(child):
     print("Successfully got into enable mode")
  else:
     print("Can't get into enable mode")
  return child


def is_Vlan(vlan):
  child = connect_SW(switch_un)
  child.sendline(' ')
  child.sendline('!')
  child.sendline('terminal length 0')
  child.expect('#')
  cmd = 'show vlan id '+str(vlan)
  child.sendline(cmd)
  i = child.expect(['not found','Ports'])
  if i==0:
    print("VLAN {0} doesn't exist".format(vlan))
    return False
  elif i==1:
    print('Vlan {0} exists!!!'.format(vlan))
    return True




def ios_conf(child):
#"""
#Use commands.txt as a collection of commands to run on ios devices.
#exit1 must exist at the last line.
#"""
    with open('/usr/local/bin/scripts/commands.txt', 'r') as commands:
         for items in commands:
             end = str('exit1')
             if 'exit1' in items:
                break
             else:
                child.sendline(items)
                child.expect('#')


def boot_config(child,target_img,run_img):
#"""
#Change the boot system file.
#target_img will be the first choice of boot image.
#run_img will be the second choice if first choice doesn't work.
#"""
    child.sendline('conf t')
    child.sendline('no boot system')
    cmd='boot system flash:'+target_img
    child.sendline(cmd)
    cmd='boot system flash:'+run_img
    child.sendline(cmd)
    child.sendline('end')
    child.sendline('wr')



def running_img(child,run_img):
#"""
#Return running ios image file name of the device
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
             if ( run_img == target_img ):
                      print(ip,'   #### Running Img : ',run_img,'   This Device is UP To DATE!!!  ###')
                      child.sendline(' ')
                      child.sendline(' ')
                      child.sendline(' ')

             break
      return run_img
   except:
      raise



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


def Upload(child,ri,fi,fs,target_img):
#"""
#ri : Running_image,
#fi : a list of images on flash drive
#fs : Free Space in flash drive
#"""
   try:
      #ri = running_img(child,run_img)
      #print('Running Imgage :  ',ri)
      #fi = flash_img(child,cur_img)
      #print('Current Img on Flash :   ',fi)
      #fs = flash_free(child,free_space)
      #print('Free Space in Falsh :   ',fs)
      print(ip, ' ri = ',ri, ' fi = ',fi,'   fs = ',fs, 'img_size = ',required_space, '  target_img = ',target_img)
      if target_img in fi:
             print(ip, 'New Target Img is already in Flash Drive !!!')
      elif ri not in s_img:
             print(ip, 'This device is not Intended for Upgrade')
      elif int(fs) < int(required_space):
             cmd = 'delete flash:'+fi[0]
             print(ip,'   Deleting ', cmd)
             child.sendline(cmd)
             child.expect('.bin]?')
             child.sendline('')
             child.expect('[confirm]')
             child.sendline('')
             print(ip,'   Uploading file... ', target_img)
             #input('Confirm ...')
             cmd = 'copy scp://t806247:summer15@10.253.103.40/'+target_img+' flash:'
             child.sendline(cmd)
             child.expect('.bin]?')
             child.sendline('')
             child.expect('[confirm]')
             child.sendline('')
             child.expect('#', timeout=60000000)
             child.sendline('')
             child.expect('#')
             print(ip,'   Uploading finished...')

      elif int(fs) > int(required_space):
             print(ip,'   Uploading file... ', target_img)
             #input('Confirm ...')
             cmd = 'copy scp://t806247:summer15@10.253.103.40/'+target_img+' flash:'
             child.sendline(cmd)
             child.expect('.bin]?')
             child.sendline('')
             child.expect('[confirm]')
             child.sendline('')
             child.expect('#', timeout=60000000)
             child.sendline('')
             child.expect('#')
             print(ip,'   Uploading finished...')

   except:
      raise


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

def logfiler(ip):
     log1 = 'home/t806247/'+ip+'.log'
     details = open(log1,"w")
     return details


def ios_config(child):
#"""
#Configure the device using ios-cmd.txt file as command input.
#child is a pointer to pexpect.spawn().
#"""
    child.sendline('!')
    child.expect('#')
    child.sendline('conf t')
    child.expect('#')
    with open("ios-cmd.txt","r") as f:
       for item in f.readlines():
          if item != 'exit1':
             child.sendline(item)
             child.expect('#')
             time.sleep(1)
          else:
             break

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


def get_line(child,command,check_string):
   child.sendline('!')
   child.expect('#')
   child.sendline(command)
   child.expect('#')
   result = child.before.splitlines()
   print(result)
   mStat = False
   for item in result:
      if check_string in result:
         match = item
         mStat = True
         return match
         break
   if not mStat:
      return False


def get_img(child,command,check_string):
   child.sendline('!')
   child.expect('#')
   child.sendline(command)
   child.expect('#')
   result = child.before.splitlines()
   print(result)
   mStat = False
   for item in result:
      if check_string in result:
         match = item
         mStat = True
         return match
         break
   if not mStat:
      return False





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



class ThreadPool(object):
    def __init__(self):
        super(ThreadPool, self).__init__()
        self.active = []
        self.lock = threading.Lock()
    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            logging.debug('Running: %s', self.active)
    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            logging.debug('Running: %s', self.active)

def f(s, pool, ip):
    logging.debug('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        pool.makeActive(name)
        """Call MAIN Function to start a process"""
        mStart_time = time.time()
        main(ip)
        now = time.time()
        print(ip, "--- %s seconds ---" % str(time.time() - mStart_time))
        pool.makeInactive(name)

