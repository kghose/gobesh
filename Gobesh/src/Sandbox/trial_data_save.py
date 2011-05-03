"""Script to demonstrate the concept of saving trial data (state) at the end
of every trial in pickled form, sequentially into the same file."""

import cPickle
import datetime

tfilename = 'trial_data.pkl'
f = open(tfilename,'w')

for n in range(100):
  trial_dict = {'trial no': n, 'random data': datetime.datetime.now()}
  cPickle.dump(trial_dict, f, protocol=cPickle.HIGHEST_PROTOCOL)
  
f.close()

f = open(tfilename,'r')
try:
  while True:
    td = cPickle.load(f)
    print td
except EOFError:
  pass
f.close()
  