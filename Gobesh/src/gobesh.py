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

class GExperiment:
  """."""
  def __init__(self, DeviceDefinitions):
    self.parent_q = mp.Queue() #The devices talk back to the main thread via this
    self.initialize_device_list(DeviceDefinitions) #
    
    #The experiment isn't running yet    
    self.host = 'localhost'
    self.port = 8080
    self.p = mp.Process(target=self.start_web_handler)
    self.p.start()

  def start_web_handler(self):
    httpd = make_server(self.host, self.port, self.web_handler)
    httpd.serve_forever()
    
  def web_handler(self, environ, start_response):
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
    html = "<html><body>"
    for dev in self.devices:
      html += "<a href='/" + dev.name + "'>" + dev.name + "</br>"
    html += "</body></html>"
    return html
  
  def device_operation(self, pth, environ):
    # Find which device it was
    this_dev = None
    for dev in self.devices:
      if dev.name == pth:
        this_dev = dev
        break

    if this_dev == None:
      html = "<html><body>No device called" + pth + "</body></html>"
      return html
    else:
      pth = shift_path_info(environ)
      if pth != None: #An attempt to trigger an event?
        self.trigger_event([this_dev.name, pth])
        
      #show the device and update variables if needed etc.
      if environ['QUERY_STRING'] != '':#We want to try and set some settings
        # Returns a dictionary containing lists as values.
        d = parse_qs(environ['QUERY_STRING'])        
        print 'Pretending to set'
      
      settings = this_dev.get_settings()
        
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

  def initialize_device_list(self, DeviceDefinitions):
    self.devices = []
    DD = DeviceDefinitions
    for key in DD.keys():
      self.devices.append(DD[key]['class'](key, self.parent_q))
    
  def run(self):
    msg = self.parent_q.get()
    print msg
    
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
