
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



def ios_config(child,configFile):
#"""
#Configure the device using ios-cmd.txt file as command input.
#child is a pointer to pexpect.spawn().
#"""
    child.sendline('!')
    child.expect('#')
    child.sendline('conf t')
    child.expect('#')
    with open(configFile,"r") as f:
       for item in f.readlines():
          if item != 'exit1':
             child.sendline(item)
             child.expect('#')
             time.sleep(1)
          else:
             break


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


