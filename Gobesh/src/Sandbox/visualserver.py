import pyglet
import multiprocessing as mp
import multiprocessing.connection as mpc
import time

class VisualServer:
  """This is written as a class to allow overriding of the central logic and to
  encapsulate some persistent shared variables."""
  def __init__(self):
    self.neutral_gray = 128
    self.max_range = 127 #needs to add up to 255 or whatever resolution we use
    self.address = ''
    self.port = 6000
    self.authkey = 'visual stimuli'
    self.listener = None
    self.remote_conn = None
    
  def wait_for_client(self):
    """Wait for a client to connect and return us the connection. Putting
    'localhost' prevents connections from outside machines."""
    print('Waiting for client')
    self.listener == None
    while self.listener == None:
      try:
        self.listener = mpc.Listener((self.address, self.port), authkey=self.authkey)
        self.remote_conn = self.listener.accept()
        print('Connection accepted from:' + self.listener.last_accepted[0] + ':%d' %(self.listener.last_accepted[1]))
      except mp.AuthenticationError:
        print('Client had wrong key')        

  def poll_command_server(self):
    """Test if we have any messages. If so return the message, otherwise return
    None."""
    msg = None
    try: 
      if self.remote_conn.poll():
        msg = self.remote_conn.recv()
    except EOFError:
      print('Lost connection to client')
      self.listener.close()
      self.listener = None
    except:
      print('Other error')
      self.listener.close()
      self.listener = None
    return msg

def server_poll(dt, server):
  """Wrapper for poll_command_server, that takes care of dropped conns etc."""
  if server.listener == None:
    server.wait_for_client()

  msg = server.poll_command_server()
  if msg is not None: 
    print msg
    if msg == 'quit':
      print 'bye'
      pyglet.app.exit()
      pyglet.clock.unschedule(server_poll)
  
if __name__ == '__main__':
  server = VisualServer()
  pyglet.clock.schedule_interval(server_poll, .1, server)
  pyglet.app.run()