#!/usr/bin/env python
"""Gobesh core
"""

from optparse import OptionParser
import logging
import sys
import time #For the timestamp and sleep function
import multiprocessing as mp #For threading

from wsgiref.simple_server import make_server
from wsgiref.util import shift_path_info
from cgi import parse_qs, escape

logger = logging.getLogger('Gobesh')

class GWebHandler:
  """A convenience base class to encapsulate the webinterface for Gobesh. This
  is inherited by GExperiment. Reduces clutter in GExperiment"""

  def run_web_server(self):
    """This should be started in a new thread."""
    self.httpd = make_server(self.host, self.port, self.web_handler)
    self.httpd.serve_forever()
    
  def web_handler(self, environ, start_response):
    """Application called when we interact with the webserver."""
    pth = shift_path_info(environ)
    if pth == '':#Root page
      response_body = self.index()
    else:
      response_body = self.device_operation(pth, environ)
    
    status = '200 OK'
    
    # Now content type is text/html
    response_headers = [('Content-Type', 'text/html'),
                   ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)
    
    return [response_body]
    
  def index(self):
    """Return a list of devices."""
    html = "<html><title>Gobesh</title><body>"
    for dev in self.devices:
      html += "<a href='/" + dev.name + "'>" + dev.name + "</br>"
    html += "</body></html>"
    return html
  
  def device_operation(self, device_name, environ):
    # Find which device it was
    this_dev = None
    for dev in self.devices:
      if dev.name == device_name:
        this_dev = dev
        break

    if this_dev == None:
      html = "<html><body>No device called" + device_name + "</body></html>"
      return html
    
    #There really is a device called this
    pth = shift_path_info(environ)
    if pth == 'trigger_event': #An attempt to trigger an event
      event = shift_path_info(environ)
      self.trigger_event([this_dev.name, event])
    
    settings = this_dev.get_settings()
      
    #show the device and update variables if needed etc.
    if environ['QUERY_STRING'] != '':#We want to try and set some settings
      # Returns a dictionary containing lists as values.
      vars_to_set = []
      d = parse_qs(environ['QUERY_STRING'])
      vars = settings['variables']
      for var in vars:
        if var[3]:
          var_value = escape(d.get(var[0],[var[4]])[0])
          vars_to_set.append([var[0], var_value])
      this_dev.set_variables(vars_to_set)
      settings = this_dev.get_settings()#Update the saved variables

    # The device display
    html = "<html><body>"  
    #Events
    events = settings['events']
    for event in events:
      html += "<a href='/" + this_dev.name + "/trigger_event/" + event[0] + "' title='" + event[1] + "'>" + event[0] + "</a></br>"
    
    html += """<form method="get" action="%s">""" %(this_dev.name)
    #Variables
    vars = settings['variables']
    for var in vars:
      if var[3]: #Editable or not?
        disabled_text = ""
      else:
        disabled_text = " disabled='disabled' "
      html += """<p>%s: <input type="text" name="%s" title="%s" value="%s" %s/></p>""" %(var[0], var[0], var[1], var[4], disabled_text)
    html += """<p><input type="submit" value="Submit"></p>"""
    html += "</form>"  
    html += "</body></html>"
    return html      
  
  def quit_server(self):
    """Don't call this from same thread that is running the server."""
    self.httpd.shutdown()

  def quit(self):
    """Reimplement this in GExperiment to shutdown devices etc."""
    pass
  
  def trigger_event(msg):
    """Reimplement this in GExperiment."""
    pass
    
class GExperiment(GWebHandler):
  """."""
  def __init__(self, StateMachine, DeviceDefinitions):
    self.parent_q = mp.Queue() #The devices talk back to the main thread via this
    self.initialize_device_list(DeviceDefinitions) #
    self.state_machine = StateMachine
    
    #The experiment isn't running yet    
    self.host = 'localhost'
    self.port = 8080
    self.httpd = make_server(self.host, self.port, self.web_handler)
    self.webhandler_process = mp.Process(target=self.httpd.serve_forever)
    self.webhandler_process.start()

  def initialize_device_list(self, DeviceDefinitions):
    self.devices = []
    DD = DeviceDefinitions
    for key in DD.keys():
      self.devices.append(DD[key]['class'](key, self.parent_q))
  
  def build_routing_table(self, DeviceDefinitions):
    """Set up a dictionary that allows us to route events and variables to the
    correct devices."""
    
  def run(self):
    """The main experiment serving loop."""
    error = False
    state = 'Wait' #Built in start state
    state_machine = self.state_machine
    get_message = self.parent_q.get
    put_message = self.parent_q.put
    while state != 'Exit' and not error: #last state
      #Handle messages
      msg = get_message()
      if msg[0] == 'event':
        this_event = msg[1] #We are expecting a string of the form <device name>.<event name>
        if state_machine[state].has_key(this_event):
          #Advance state and put state events into the queue
          put_message(['event', state + '.exit'])
          state = state_machine[state][this_event]
          put_message(['event', state + '.enter'])
      elif 
    
    
    #Clean up and get out
    self.quit()

    if error:
      print 'There were errors'  

  def trigger_event(self, msg):
    """Reimplement this in GExperiment."""
    self.parent_q.put(['event', msg[0] + '.' + msg[1]])


  def quit(self):
    for device in self.devices:
      device.quit()

    self.webhandler_process.terminate()#Drastic, couldn't get shutdown to work
    #self.httpd.shutdown()
    print 'Quit server'


#    self.quit_server()
    
#def quit_devices(devices):
#  for device in devices:
#    device.quit() #TODO: Gotta fix state_event and variables
#  
#def parse_command_line_args():
#  parser = OptionParser(version="%prog 1.0")
#  parser.add_option("-d", "--debug_level", 
#                    dest="debug_level", default="debug",
#                    help="Set debug level. 'debug','info','warning','error','critical' [%default]")
#  parser.add_option("-c", "--configuration_file", 
#                    dest="configuration_file", default="demo_experiment_config.py", 
#                    help="Configuration file to load [%default]")  
#  parser.add_option("-l", "--log_file", 
#                    dest="log_file", default="gobeshserver.log", 
#                    help="Log file [%default]")
#  
#  (options, args) = parser.parse_args()
#  return options, args
#
#def setup_logging(options):
#  #Logging stuff
#  LOG_FILENAME = options.log_file
#  LEVELS = {'debug': logging.DEBUG,
#            'info': logging.INFO,
#            'warning': logging.WARNING,
#            'error': logging.ERROR,
#            'critical': logging.CRITICAL}
#  
#  level = LEVELS.get(options.debug_level, logging.NOTSET)
#  
#  logging.basicConfig(filename=LOG_FILENAME, 
#                      format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#                      level=level)  
#
#
#def server_loop(options, 
#                state_machine, routing_matrix, devices):
#  parent_q =  #The devices talk back to the main thread via this
#
#
#def gobesh_web_server():
#  def server():
#    httpd = make_server('localhost', 8051, gobesh_web_handler)
#    httpd.serve_forever()
#  
#  p = mp.Process(target=server)
#  p.start()
#
#  return p
#
#def gobesh_web_handler(environ, start_response):
#  'PATH_INFO'
#
#    
#def start_experiment_server(ExperimentName, StateMachine, DeviceDefinitions):
#  """Entry point to call from our experiment script."""
#  options, args = parse_command_line_args()
#  setup_logging(options)
#  expt_def, error = instantiate_experiment(StateMachine, DeviceDefinitions)
#  if not error:
#    error = initialize_devices(options, expt_def)
#  if not error:
#    server_loop(options, expt_def)
#  else:
#    print 'There were errors setting up. Please check logging file ' + options.log_file
