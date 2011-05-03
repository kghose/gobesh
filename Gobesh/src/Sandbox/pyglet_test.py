import multiprocessing as mp
import logging #We should make use of the logging function
logger = logging.getLogger('Gobesh.'+__name__)

logging.basicConfig(filename='eraseme.log', 
                    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.DEBUG)  
  
#import wx #For the MilliSleep
#default_sleep = wx.MilliSleep
import time
  
def server():
  exec open('pyglet_test_import.py')

  dev = eval('avkm.GAVKMDevice()')

#  dev = avkm.GAVKMDevice()
  dev.initialize()
  return dev
  
dev = server()

for n in range(1000):
  dev.poll(timestamp=0, state_event=None, input_vars=None)
  time.sleep(.001)
  
dev.p.join()


