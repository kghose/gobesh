import multiprocessing as mp
#import wx

def run():
  import pyglet
  #pyglet.options["shadow_window"] = False
    
  w = pyglet.window.Window(resizable=True)
  while not w.has_exit:
    w.dispatch_events()
  w.close()


p = mp.Process(target=run)
p.start()
p.join()