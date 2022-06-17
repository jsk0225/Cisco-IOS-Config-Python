#!/usr/bin/env python
"""
James Jung 2018-09-24- Python
Script to connect to multiple switches, add a specific command and logout.
###Variables to Set:
  s_img : If the device is running on this image, the ios will be replaced.
  target_img : self explanatory
  required_space : self explanatory
### External Files used
device_list.txt : each line is an ip address to run this script against
Details.log : Logging file

Test Script : pexpect_test.py
Release Script : ios_upgrade_c.py
"""
import os
import sys
import pexpect
import subprocess
import time
import logging
import re
import threading
#import jsk

#dl = 'hosts10'
dl = raw_input('Device List File : ')
device_list = open(dl, 'r')
count_lines = 0

start_time = time.time()
#details = open("/usr/local/bin/scripts/Details.log","w")
#log1 = 'hosts10.log'
#log1 = raw_input('Log File : ')
#details = open(log1,"w")

logger = logging.getLogger('info_logger')
logger.setLevel(logging.DEBUG)
#Create file handler which logs even debug messages
fh = logging.FileHandler('Info.log', 'w')
fh.setLevel(logging.DEBUG)
#Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
#Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
#Add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

#Switch username
switch_un = "t806247"
#Switch password
switch_pw = "summer16"
s_img = ["c800-universalk9-mz.SPA.154-3.M3.bin", "c800-universalk9-mz.SPA.152-4.M4.bin", "c800-universalk9-mz.SPA.153-3.M.bin", "c800-universalk9-mz.SPA.156-2.T1.bin", "c800-universalk9-mz.SPA.153-3.M5.bin", "c800-universalk9-mz.SPA.152-4.M4.bin", "c800-universalk9-mz.SPA.152-4.M6.bin", "c800-universalk9-mz.SPA.154-3.M7.bin", "c800-universalk9-mz.SPA.153-3.M6.bin"]

#s_img = ["c860vae-advsecurityk9-mz.152-4.M9.bin","c860vae-advsecurityk9-mz.152-4.M9.bin","c860vae-ipbasek9-mz.152-4.M5.bin","c860vae-ipbasek9-mz.152-4.M3.bin","c860vae-ipbasek9-mz.152-4.M4.bin","c860vae-ipbasek9-mz.153-3.M2.bin","c860vae-advsecurityk9-mz.152-4.M4.bin","c860vae-advsecurityk9-mz.152-4.M5.bin","c860vae-advsecurityk9-mz.152-4.M6.bin","c860vae-ipbasek9-mz.152-4.M3.bin","c860vae-ipbasek9-mz.152-4.M4.bin","c860vae-advsecurityk9-mz.153-1.T4.bin"]
run_img = " "
cur_img = ['a','a','a','a']
#s_img = raw_input('IOS To be replaced..[a,b,..]. : ')
#target_img = 'c860vae-advsecurityk9-mz.154-3.M10.bin'
#target_img = "c860vae-advsecurityk9-mz.154-3.M10.bin"
target_img = "/home/t806247/c800-universalk9-mz.SPA.154-3.M10.bin"
required_space = os.path.getsize(target_img)
free_space = 10
#target_img = raw_input('New IOS ... : ')
#required_space = int(raw_input('New IOS File Size : '))

#required_space = 39615500
#Function that will be called to send commands to the switch

def running_img(child,run_img,ip):
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

def flash_img(child,cur_img,ip):
   try:
      child.sendline(' ')
      child.expect('#')
      child.setecho(False)
      child.sendline('show flash:')
      ji = child.expect(['free','used','No space info'],timeout=15)
      if ji == 2:
        return  'None'
      else:
         print(ip, '       child.before  =  ',child.before,'     child.match =            ',child.match,'               child.after =        ',child.after)
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

def flash_free(child,free_space,ip):
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


def Upload(child,ri,fi,fs,ip):
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
             cmd = 'copy scp://t806247:summer16@10.253.103.40/'+target_img+' flash:'
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
             cmd = 'copy scp://t806247:summer16@10.253.103.40/'+target_img+' flash:'
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
             child.line('c')
             child.line('c')
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
             child.line('c')
             child.line('c')
             print(ip, '\nCheck the device. Can\'t go into Enable mode.')
             return False
       elif i == 3:
          child.sendline(switch_pw)
          j = child.expect(['#','assword:'])
          if j == 0:
             return True
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
     log1 = '/usr/local/bin/scripts/logs/'+ip+'.log'
     details = open(log1,"w")
     return details

def main(ip):
        try:
                print('\n\n')
                print(ip,'   Trying a remote device ..')
                child = pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' % (switch_un, ip),maxread=10000)
                child.delaybeforesend = 1
                child.logfile = logfiler(ip)
                child.timeout = 1500
                cur_img = ['a','a','a','a']
                i = child.expect(['Password:',pexpect.TIMEOUT,pexpect.EOF,'Connection refused','Connection timed out','Connection refused by server','Are you sure you want to continue connecting (yes/no)?'])
                if i == 0:
                        child.sendline(switch_pw)
                        if(enable(child)):
                           #print("In Enable Mode")
                           child.sendline('terminal length 0')
                           child.expect('#')
                           fi = flash_img(child,cur_img,ip)
                           print(ip,'Current Img on Flash :   ',fi)
                           if target_img in fi:
                              print(ip, 'Target img is already in Flash Drive')
                           elif fi == 'None':
                              child.sendline('!')
                              print(ip, 'Error opening flash: ... No space information available')
                           else:
                              fs = flash_free(child,free_space,ip)
                              print(ip,'Free Space in Falsh :   ',fs)
                              ri = running_img(child,run_img,ip)
                              print(ip,'Running Imgage :  ',ri)
                              Upload(child,ri,fi,fs,ip)
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



cr = input('Concurrent # of Jobs [Default = 5] : ')
if cr == '':
   concurrent = 5
else:
   concurrent = int(cr)
ts = input('Estimate time of one job [Default = 30] : ')
if ts == '':
   tsleep = 30
else:
   tsleep = int(ts)



with open(os.devnull, "wb") as limbo:
    if __name__ == '__main__':
        pool = ThreadPool()
        s = threading.Semaphore(concurrent)
        i = 0
        for ip in device_list:
                        i += 1

                        result=subprocess.Popen(["ping", "-c", "1", "-n", "-W", "2", ip],
                                        stdout=limbo, stderr=limbo).wait()
                        if result:
                                        logger.info( '%s is not an active switch, skipping', ip)
                                        print( '%s is not an active switch, skipping -X_X-' % ip)
                        else:
                                        t = threading.Thread(target=f, name='thread_'+str(ip), args=(s, pool, ip))
                                        t.start()
                                        if (i % concurrent) == 0:
                                             time.sleep(tsleep)
                                        else:
                                             time.sleep(5)


#For loop that will loop through switches in a specific range
#with open(os.devnull, "wb") as limbo:
        #for n in xrange(3, 20):
                #ip="10.23.192.{0}".format(n)
                #result=subprocess.Popen(["ping", "-c", "1", "-n", "-W", "2", ip],
                        #stdout=limbo, stderr=limbo).wait()
                #if result:
                        #logger.info( '%s is not an active switch, skipping', ip)
                        #print( '%s is not an active switch, skipping -X_X-' % ip)
                #else:
                        #http_secure_server(ip)


device_list.close()
details.close()
print(" Congratulations!!! The program successfully completed all the devices in the list....")
print("--- %s seconds ---" % str(time.time() - start_time))

