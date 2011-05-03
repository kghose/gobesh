"""Testing out different way of doing events without having polling loop."""

import multiprocessing as mp
import random
import time

class device:
  def __init__(self, name, queue_to_parent):
    """conn_to_parent - this is the ."""
    self.name = name
    self.queue_from_parent = mp.Queue()
    self.queue_to_parent = queue_to_parent
    self.p = mp.Process(target=self.deviceloop)
    self.p.start()
    
  def deviceloop(self):
    keep_running = True
    while keep_running:
      r = random.random()
      time.sleep(r)
      self.queue_to_parent.put([self.name, time.time()])
      if not self.queue_from_parent.empty():
        msg = self.queue_from_parent.get()
        if msg == 'quit':
          keep_running = False
    
    print self.name, 'Quitting'

  def quit(self):
    self.p.join()

parent_q = mp.Queue() #The devices talk back to the main thread via this
names = ['harry','sally','tom','dick']
n_events = 20

d = [None]*len(names)
for n,name in enumerate(names):
  d[n] = device(name, parent_q)
  
while n_events > 0:
  msg = parent_q.get()
  print msg, time.time() - msg[1]
  n_events -= 1
  
for n in range(len(names)):
  d[n].queue_from_parent.put('quit')

for this_d in d:
  this_d.quit()
  